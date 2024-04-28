import os
import hashlib
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import io
import requests

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Запуск в фоновом режиме без открытия окна браузера
    return webdriver.Chrome(options=options)

def download_image(url, filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with Image.open(io.BytesIO(response.content)) as img:
            if img.size[0] * img.size[1] > 1024 * 1024:  # Порог размера изображения, например 1 мегапиксель
                img.thumbnail((1024, 1024))  # Меняем размер изображения
            img.save(filename, format='JPEG')
        print(f"Изображение {url} успешно сохранено как {filename}")
    else:
        print(f"Не удалось загрузить изображение {url}")

def parse(url):
    driver = setup_driver()
    driver.get(url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "t-store__card__imgwrapper"))
    )

    if not os.path.exists('images'):
        os.makedirs('images')

    imgwrappers = driver.find_elements(By.CLASS_NAME, "t-store__card__imgwrapper")
    all_images = [element.find_element(By.CLASS_NAME, "js-product-img").get_attribute('data-original') for element in imgwrappers]
    driver.quit()

    executor = ThreadPoolExecutor(max_workers=5)
    for image_url in all_images:
        if image_url:  # Проверяем, что src не None
            image_hash = hashlib.md5(image_url.encode('utf-8')).hexdigest()
            filename = f"images/{image_hash}.jpg"
            if not os.path.exists(filename):  # Проверяем, было ли уже скачано изображение
                executor.submit(download_image, image_url, filename)
    executor.shutdown(wait=True)