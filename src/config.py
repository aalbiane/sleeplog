import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Загрузка .env
load_dotenv()

DB_PATH = os.getenv("DB_PATH", "sleep_data.db")
TIMEZONE = os.getenv("TIMEZONE", "Europe/Moscow")

# Настройка логирования
LOG_FILE = Path("app.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def get_logger():
    return logging.getLogger(__name__)