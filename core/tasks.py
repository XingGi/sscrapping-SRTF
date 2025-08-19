# core/tasks.py

import time
from celery import shared_task
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from .models import Video, Comment

@shared_task
def scrape_youtube_videos_task(keyword, scroll_pages=2):
    """
    Celery task untuk melakukan scraping data video YouTube di latar belakang.
    """
    print(f"🚀 Memulai Celery task untuk keyword: '{keyword}'")

    options_config = webdriver.ChromeOptions()
    options_config.add_argument("--headless") # PENTING: Jalankan di background
    options_config.add_argument("--log-level=3")
    options_config.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options_config)
    driver.maximize_window()

    try:
        print("1. Membuka YouTube...")
        driver.get("https://www.youtube.com")

        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "search_query"))
        )
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)
        print("   -> Berhasil melakukan pencarian.")

        print(f"2. Melakukan scroll sebanyak {scroll_pages} halaman...")
        for i in range(scroll_pages):
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(3)
            print(f"   -> Scroll ke-{i+1} selesai.")

        print("3. Mengambil semua data video yang terlihat...")
        video_containers = driver.find_elements(By.CSS_SELECTOR, "div#dismissible")
        
        videos_found = []
        for container in video_containers:
            try:
                title_element = container.find_element(By.ID, "video-title")
                video_url = title_element.get_attribute('href')
                title = title_element.text

                if not video_url or "watch?v=" not in video_url:
                    continue
                
                channel_info_container = container.find_element(By.ID, "channel-info")
                channel_name = channel_info_container.find_element(By.CSS_SELECTOR, "a.yt-simple-endpoint").text
                
                if video_url not in [v['url'] for v in videos_found] and channel_name:
                    videos_found.append({
                        'title': title,
                        'channel': channel_name,
                        'url': video_url
                    })
            except NoSuchElementException:
                continue
        
        print(f"   -> Ditemukan {len(videos_found)} video unik.")

        print("4. Menyimpan data ke database...")
        saved_count = 0
        for video_data in videos_found:
            obj, created = Video.objects.update_or_create(
                video_url=video_data['url'],
                defaults={
                    'title': video_data['title'],
                    'channel_name': video_data['channel']
                }
            )
            if created:
                saved_count += 1
        
        print(f"   -> Berhasil menyimpan {saved_count} video baru.")
        return f"Proses selesai. Berhasil menyimpan {saved_count} video baru untuk keyword '{keyword}'."

    except Exception as e:
        print(f"Terjadi error: {e}")
        return f"Gagal menjalankan scraping untuk keyword '{keyword}'. Error: {e}"
    finally:
        print("✅ Task selesai.")
        driver.quit()
        
@shared_task
def scrape_youtube_comments_task(video_limit=5, scroll_count=3, max_comments_per_video=20):
    """
    Celery task untuk scrape komentar dari video yang ada di database.
    """
    print(f"🚀 Memulai Celery task untuk scraping komentar...")

    videos_to_scrape = Video.objects.filter(comments__isnull=True)[:video_limit]
    
    if not videos_to_scrape:
        print("👍 Semua video sudah memiliki komentar. Tidak ada pekerjaan.")
        return "Semua video sudah memiliki komentar."

    print(f"Menemukan {len(videos_to_scrape)} video untuk di-scrape komentarnya.")

    options_config = webdriver.ChromeOptions()
    options_config.add_argument("--headless")
    options_config.add_argument("--log-level=3")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options_config)

    total_saved_comments = 0
    try:
        for video in videos_to_scrape:
            print(f"--- Mengambil komentar untuk: '{video.title[:50]}...' ---")
            driver.get(video.video_url)
            try:
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#comments")))
                
                for i in range(scroll_count):
                    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                    time.sleep(2)
                
                comment_elements = driver.find_elements(By.CSS_SELECTOR, "ytd-comment-thread-renderer")
                
                saved_count = 0
                for element in comment_elements[:max_comments_per_video]:
                    try:
                        username = element.find_element(By.ID, "author-text").text
                        text = element.find_element(By.ID, "content-text").text
                        comment_url_element = element.find_element(By.CSS_SELECTOR, "a.yt-simple-endpoint")
                        comment_url = comment_url_element.get_attribute('href')

                        if username and text:
                            Comment.objects.get_or_create(
                                video=video,
                                username=username,
                                text=text,
                                defaults={'comment_url': comment_url, 'platform': 'YT'}
                            )
                            saved_count += 1
                    except NoSuchElementException:
                        continue
                
                total_saved_comments += saved_count
                print(f"   -> Berhasil menyimpan {saved_count} komentar baru.")
            except TimeoutException:
                print(f"   -> Gagal menemukan bagian komentar untuk video ini.")
                continue
    except Exception as e:
        print(f"Terjadi error: {e}")
        return f"Gagal menjalankan scraping komentar. Error: {e}"
    finally:
        driver.quit()
        print("✅ Task komentar selesai.")
    
    return f"Proses selesai. Berhasil menyimpan total {total_saved_comments} komentar baru."