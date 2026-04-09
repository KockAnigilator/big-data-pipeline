import logging
import os
from .config import LOG_DIR

def setup_logger(name: str, log_file: str, level=logging.INFO):
    os.makedirs(LOG_DIR, exist_ok=True)
    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
    
    handler = logging.FileHandler(os.path.join(LOG_DIR, log_file), encoding='utf-8')
    handler.setFormatter(formatter)
    
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(console)
    return logger