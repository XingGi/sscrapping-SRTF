# test_scraper.py (Hybrid: Working Search + Robust Scraping Logic)

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -- Konfigurasi Selenium --
options = webdriver.ChromeOptions()
options.add_argument("--log-level=3")
options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.maximize_window()

# -- Variabel --
KEYWORD = "tutorial vue js untuk pemula"
MAX_VIDEOS = 5

try:
    print("1. Membuka YouTube...")
    driver.get("https://www.youtube.com")

    # --- BAGIAN 1: MENGGUNAKAN METODE PENCARIAN LAMA YANG BEKERJA ---
    print("2. Menunggu dan mencari kolom pencarian (Metode Awal)...")
    # Menggunakan selector NAME 'search_query' yang terbukti bekerja sebelumnya
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "search_query"))
    )

    print("3. Mengetik keyword dan memulai pencarian...")
    search_box.send_keys(KEYWORD)
    search_box.send_keys(Keys.RETURN)
    
    # --- BAGIAN 2: MENGGUNAKAN LOGIKA SCRAPING BARU YANG AKURAT ---
    print("4. Menunggu hasil pencarian muncul...")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "video-title"))
    )

    print("5. Mengambil data video...")
    title_elements = driver.find_elements(By.ID, "video-title")

    found_videos = []
    for title_element in title_elements:
        if len(found_videos) >= MAX_VIDEOS:
            break
        try:
            video_url = title_element.get_attribute('href')
            if not video_url or "watch?v=" not in video_url:
                continue

            container = title_element.find_element(By.XPATH, "./ancestor::div[@id='dismissible']")
            channel_name = container.find_element(By.CSS_SELECTOR, "#channel-info a").text
            title = title_element.text

            if title and channel_name:
                found_videos.append({"title": title, "channel": channel_name, "url": video_url})
        except Exception:
            continue
    
    if found_videos:
        print("\n" + "="*10 + " ✅ DATA BERHASIL DIAMBIL " + "="*10)
        for video in found_videos:
            print(f"Judul: {video['title']}\nChannel: {video['channel']}\nURL: {video['url']}\n" + "-"*20)
    else:
        print("\n--- ❌ TIDAK ADA DATA VIDEO YANG SESUAI DITEMUKAN ---")

except Exception as e:
    print(f"!! Terjadi error tak terduga: {e}")
finally:
    print("\n--- Script Selesai ---")
    time.sleep(5) 
    driver.quit()