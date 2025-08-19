# core/management/commands/scrape_comments.py

import time
from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dateutil.parser import parse as date_parse

from core.models import Video, Comment

class Command(BaseCommand):
    help = 'Scrape comments from videos in the database that have no comments yet.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=5, help='Limit the number of videos to process in one run.')
        parser.add_argument('--scrolls', type=int, default=3, help='How many times to scroll down to load comments.')
        parser.add_argument('--max-comments', type=int, default=20, help='Maximum number of comments to scrape per video.')

    def handle(self, *args, **options):
        video_limit = options['limit']
        scroll_count = options['scrolls']
        max_comments_per_video = options['max_comments']

        self.stdout.write(self.style.SUCCESS("🚀 Memulai scraper komentar..."))

        # 1. Ambil video yang belum punya komentar
        videos_to_scrape = Video.objects.filter(comments__isnull=True)[:video_limit]
        
        if not videos_to_scrape:
            self.stdout.write(self.style.SUCCESS("👍 Semua video sudah memiliki komentar. Tidak ada pekerjaan."))
            return

        self.stdout.write(f"Menemukan {len(videos_to_scrape)} video untuk di-scrape komentarnya.")

        # -- Konfigurasi Selenium --
        options_config = webdriver.ChromeOptions()
        # options_config.add_argument("--headless") # Aktifkan jika sudah stabil
        options_config.add_argument("--log-level=3")
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options_config)

        try:
            for video in videos_to_scrape:
                self.stdout.write(f"\n--- Mengambil komentar untuk: '{video.title[:50]}...' ---")
                driver.get(video.video_url)

                try:
                    # 2. Lakukan scrolling untuk memuat komentar
                    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#comments")))
                    self.stdout.write("   -> Halaman komentar ditemukan, melakukan scroll...")
                    
                    for i in range(scroll_count):
                        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                        time.sleep(2) # Waktu tunggu agar komentar baru termuat
                        self.stdout.write(f"   -> Scroll ke-{i+1}/{scroll_count}...")
                    
                    # 3. Ambil semua elemen komentar
                    comment_elements = driver.find_elements(By.CSS_SELECTOR, "ytd-comment-thread-renderer")
                    self.stdout.write(f"   -> Menemukan {len(comment_elements)} elemen komentar.")

                    # 4. Ekstrak data dan simpan
                    saved_count = 0
                    for element in comment_elements[:max_comments_per_video]:
                        try:
                            username = element.find_element(By.ID, "author-text").text
                            text = element.find_element(By.ID, "content-text").text
                            
                            # --- LOGIKA BARU UNTUK MENGAMBIL TANGGAL & URL ---
                            header_element = element.find_element(By.CSS_SELECTOR, "div#header-author")
                            comment_url_element = header_element.find_element(By.CSS_SELECTOR, "a.yt-simple-endpoint")
                            comment_url = comment_url_element.get_attribute('href')
                            
                            # Mengambil teks tanggal seperti "3 days ago" atau "1 year ago"
                            date_text = comment_url_element.text.strip()
                            
                            # (Untuk saat ini kita simpan sebagai teks, parsing akan lebih kompleks)
                            # Di masa depan kita bisa gunakan library seperti 'dateparser' untuk mengubahnya
                            
                            if username and text:
                                Comment.objects.get_or_create(
                                    video=video,
                                    username=username,
                                    text=text,
                                    comment_url=comment_url,
                                    defaults={
                                        'platform': 'YT', # <-- MENYIMPAN PLATFORM
                                        # Untuk sementara, kita bisa isi comment_date dengan tanggal scrape
                                        # Karena mengambil tanggal relatif ("3 days ago") butuh library tambahan
                                        'comment_date': None 
                                    }
                                )
                                saved_count += 1
                        except NoSuchElementException:
                            continue
                    
                    self.stdout.write(self.style.SUCCESS(f"   -> Berhasil menyimpan {saved_count} komentar baru."))

                except TimeoutException:
                    self.stdout.write(self.style.WARNING("   -> Gagal menemukan bagian komentar (mungkin dinonaktifkan). Melewati..."))
                    continue

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Terjadi error tak terduga: {e}"))
        finally:
            self.stdout.write("\n✅ Script komentar selesai.")
            driver.quit()