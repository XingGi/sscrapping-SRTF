# core/management/commands/scrape_youtube.py

import time
from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import model dari aplikasi 'core' Anda
from core.models import Video, Comment # Pastikan model Anda sudah didefinisikan

class Command(BaseCommand):
    help = 'Scrape video data from YouTube based on a keyword'

    def add_arguments(self, parser):
        parser.add_argument('keyword', type=str, help='The keyword to search for on YouTube')
        parser.add_argument('--pages', type=int, default=2, help='How many pages to scroll down')

    def handle(self, *args, **options):
        keyword = options['keyword']
        scroll_pages = options['pages']

        self.stdout.write(self.style.SUCCESS(f"🚀 Memulai scraper untuk keyword: '{keyword}'"))

        # -- Konfigurasi Selenium --
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless") # Aktifkan jika sudah yakin stabil
        options.add_argument("--log-level=3")
        options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()

        try:
            # --- TAHAP 1: NAVIGASI DAN PENCARIAN ---
            self.stdout.write("1. Membuka YouTube...")
            driver.get("https://www.youtube.com")

            # Menggunakan selector yang terbukti paling stabil (NAME)
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "search_query"))
            )
            search_box.send_keys(keyword)
            search_box.send_keys(Keys.RETURN)
            self.stdout.write(self.style.SUCCESS("   -> Berhasil melakukan pencarian."))

            # --- TAHAP 2: SCROLLING UNTUK MEMUAT LEBIH BANYAK VIDEO ---
            self.stdout.write(f"2. Melakukan scroll sebanyak {scroll_pages} halaman...")
            for i in range(scroll_pages):
                driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                time.sleep(3) # Beri waktu untuk video baru termuat
                self.stdout.write(f"   -> Scroll ke-{i+1} selesai.")

            # --- TAHAP 3: PENGAMBILAN DATA (SCRAPING) ---
            self.stdout.write("3. Mengambil semua data video yang terlihat...")
            # Menargetkan 'kotak' pembungkus yang paling konsisten
            video_containers = driver.find_elements(By.CSS_SELECTOR, "div#dismissible")
            
            if not video_containers:
                self.stdout.write(self.style.WARNING("   -> Tidak ada video yang ditemukan. Coba keyword lain."))
                return

            videos_found = []
            for container in video_containers:
                try:
                    # Di dalam setiap 'kotak', cari judul, url, dan channel
                    title_element = container.find_element(By.ID, "video-title")
                    video_url = title_element.get_attribute('href')
                    title = title_element.text

                    # Hanya proses video valid (bukan playlist atau channel)
                    if not video_url or "watch?v=" not in video_url:
                        continue
                    
                    channel_info_container = container.find_element(By.ID, "channel-info")
                    channel_name = channel_info_container.find_element(By.CSS_SELECTOR, "a.yt-simple-endpoint").text
                    
                    # Cek duplikasi sebelum menambahkan
                    if video_url not in [v['url'] for v in videos_found] and channel_name:
                        videos_found.append({
                            'title': title,
                            'channel': channel_name,
                            'url': video_url
                        })
                except NoSuchElementException:
                    continue
            
            self.stdout.write(self.style.SUCCESS(f"   -> Ditemukan {len(videos_found)} video unik dengan nama channel."))

            # --- TAHAP 4: MENYIMPAN KE DATABASE ---
            self.stdout.write("4. Menyimpan data ke database PostgreSQL...")
            saved_count = 0
            for video_data in videos_found:
                # 'update_or_create' mencegah data duplikat berdasarkan video_url
                obj, created = Video.objects.update_or_create(
                    video_url=video_data['url'],
                    defaults={
                        'title': video_data['title'],
                        'channel_name': video_data['channel']
                    }
                )
                if created:
                    saved_count += 1
            
            self.stdout.write(self.style.SUCCESS(f"   -> Berhasil menyimpan {saved_count} video baru."))

        except TimeoutException:
            self.stdout.write(self.style.ERROR("Error: Halaman terlalu lama dimuat atau elemen penting tidak ditemukan."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Terjadi error tak terduga: {e}"))
        finally:
            self.stdout.write("✅ Script selesai.")
            driver.quit()