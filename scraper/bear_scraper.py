import os
import re
import time
import logging
import requests
from bs4 import BeautifulSoup
from PIL import Image
import io
from utils.config import DATA_DIR, BEAR_CLASSES, MIN_IMAGES_PER_CLASS, HEADERS
from utils.logger import setup_logger

import sys
# Добавляем корневую папку проекта в PYTHONPATH, чтобы видеть папку utils/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


logger = setup_logger("scraper", "scraper.log")

class BearImageScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.dataset_dir = os.path.join(DATA_DIR, "dataset")

    def setup_dirs(self):
        """Программное создание структуры папок"""
        for bear_type in BEAR_CLASSES:
            os.makedirs(os.path.join(self.dataset_dir, bear_type), exist_ok=True)
            logger.info(f"Создана директория: {os.path.join(self.dataset_dir, bear_type)}")

    def fetch_image_urls(self, query: str, limit: int = 600) -> list[str]:
        """Поиск URL изображений через Wikimedia Commons (разрешён для образовательных целей)"""
        url = f"https://commons.wikimedia.org/w/index.php?search={query.replace(' ', '+')}&title=Special:MediaSearch&type=image"
        urls = []
        try:
            logger.info(f"🔍 Поиск изображений: {query}")
            resp = self.session.get(url, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Ищем все ссылки на изображения .jpg/.jpeg
            links = soup.find_all("a", href=re.compile(r"\.(jpg|jpeg)$", re.I))
            for link in links:
                href = link.get("href", "")
                if href.startswith("https://upload.wikimedia.org"):
                    urls.append(href)
        except Exception as e:
            logger.error(f"Ошибка при поиске URL: {e}")
        return list(set(urls))[:limit]

    def download_and_validate(self, url: str, save_path: str) -> bool:
        """Скачивание, проверка целостности и сохранение"""
        try:
            resp = self.session.get(url, timeout=25)
            resp.raise_for_status()
            
            # Валидация через PIL
            img = Image.open(io.BytesIO(resp.content))
            img.verify()
            
            # Сохраняем только если это реальный валидный файл
            with open(save_path, "wb") as f:
                f.write(resp.content)
                
            logger.debug(f"Сохранено: {save_path} ({img.size[0]}x{img.size[1]})")
            return True
        except Exception as e:
            logger.warning(f"Пропущен битый/недоступный файл: {e}")
            if os.path.exists(save_path):
                os.remove(save_path)
            return False

    def run(self):
        """Основной конвейер скрапинга"""
        self.setup_dirs()
        
        for bear_type in BEAR_CLASSES:
            query = "polar bear" if bear_type == "polar" else "brown bear"
            logger.info(f"=== Начинаем сбор: {bear_type} ({query}) ===")
            
            urls = self.fetch_image_urls(query)
            if not urls:
                logger.error(f"Не удалось найти URL для {bear_type}. Проверьте сеть.")
                continue

            count = 0
            idx = 0
            for url in urls:
                if count >= MIN_IMAGES_PER_CLASS:
                    break
                    
                save_path = os.path.join(self.dataset_dir, bear_type, f"{idx:04d}.jpg")
                if self.download_and_validate(url, save_path):
                    count += 1
                    idx += 1
                    if count % 50 == 0:
                        logger.info(f"[{bear_type}] Загружено: {count}/{MIN_IMAGES_PER_CLASS}")
                        
                time.sleep(0.3)  # Вежливая задержка между запросами

            if count < MIN_IMAGES_PER_CLASS:
                logger.warning(f"Собрано только {count}/{MIN_IMAGES_PER_CLASS} для {bear_type}")
            else:
                logger.info(f"{bear_type}: успешно собрано {count} полноразмерных изображений")

if __name__ == "__main__":
    scraper = BearImageScraper()
    scraper.run()