import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urlunsplit

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration
TARGET_URL = "https://www.adampaquettemtg.com"  # Use a gallery page
OUTPUT_FOLDER = "download_images"

# Set up headless Chrome
options = Options()
options.headless = True

# Set up driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Create output folder
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def clean_image_url(url):
    split_url = urlsplit(url)
    return urlunsplit((split_url.scheme, split_url.netloc, split_url.path, '', ''))

def scroll_to_bottom(pause_time=1.5, max_attempts=15):
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    for attempt in range(max_attempts):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print(f"Scrolling complete after {attempt + 1} attempts.")
            break
        last_height = new_height

def scrape_images():
    driver.get(TARGET_URL)

    # Scroll to load all lazy images
    scroll_to_bottom()

    # Parse loaded HTML
    soup = BeautifulSoup(driver.page_source, "html.parser")

    images = set()
    for img_tag in soup.find_all("img"):
        img_url = img_tag.get("data-src") or img_tag.get("src")
        if img_url and "images.squarespace-cdn.com" in img_url:
            full_res_url = clean_image_url(img_url)
            images.add(full_res_url)

    print(f"Found {len(images)} images.")
    for img_url in images:
        filename = os.path.basename(urlsplit(img_url).path)
        filepath = os.path.join(OUTPUT_FOLDER, filename)

        print(f"Downloading: {img_url}")
        try:
            img_data = requests.get(img_url).content
            with open(filepath, "wb") as f:
                f.write(img_data)
        except Exception as e:
            print(f"Failed to download {img_url}: {e}")

    print("Download complete.")

# Run
scrape_images()
driver.quit()
