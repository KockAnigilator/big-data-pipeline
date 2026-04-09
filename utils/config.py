import os

# Пути проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Kafka
KAFKA_TOPIC = "raw-data"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

# HDFS
HDFS_BASE_PATH = "/user/cloudera/raw_data"
HDFS_REALTIME_PATH = os.path.join(HDFS_BASE_PATH, "realtime")
HDFS_BATCH_PATH = os.path.join(HDFS_BASE_PATH, "batch")

# Скрапинг
BEAR_CLASSES = ["polar", "brown"]
MIN_IMAGES_PER_CLASS = 300
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}