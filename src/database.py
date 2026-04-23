import sqlite3
import json
from datetime import datetime
from pathlib import Path
from src.config import DB_PATH, get_logger

logger = get_logger()

def init_db():
    """Создание таблицы, если её нет"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sleep_entries (
                date TEXT PRIMARY KEY,
                bedtime TEXT NOT NULL,
                wakeup_time TEXT NOT NULL,
                sleep_hours REAL NOT NULL,
                sleep_quality INTEGER NOT NULL,
                morning_energy INTEGER NOT NULL,
                factors_json TEXT NOT NULL,
                notes TEXT
            )
        """)
    logger.info("База данных инициализирована")

def save_entry(entry):
    """Сохранение или обновление записи"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO sleep_entries 
                (date, bedtime, wakeup_time, sleep_hours, sleep_quality, 
                 morning_energy, factors_json, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry["date"],
                entry["bedtime"],
                entry["wakeup_time"],
                entry["sleep_hours"],
                entry["sleep_quality"],
                entry["morning_energy"],
                json.dumps(entry["factors"], ensure_ascii=False),
                entry.get("notes", "")
            ))
        logger.info(f"Запись сохранена для даты {entry['date']}")
    except Exception as e:
        logger.error(f"Ошибка сохранения записи: {e}")
        raise

def get_entry(date):
    """Получить запись за конкретную дату"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT * FROM sleep_entries WHERE date = ?", (date,)
        )
        row = cur.fetchone()
        if row:
            entry = dict(row)
            entry["factors"] = json.loads(entry["factors_json"])
            del entry["factors_json"]
            return entry
    return None

def get_entries_for_period(start_date, end_date):
    """Получить записи за период (даты в формате YYYY-MM-DD)"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT * FROM sleep_entries WHERE date BETWEEN ? AND ? ORDER BY date",
            (start_date, end_date)
        )
        rows = cur.fetchall()
        entries = []
        for row in rows:
            entry = dict(row)
            entry["factors"] = json.loads(entry["factors_json"])
            del entry["factors_json"]
            entries.append(entry)
    return entries

def get_all_entries():
    """Все записи для экспорта"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM sleep_entries ORDER BY date")
        rows = cur.fetchall()
        entries = []
        for row in rows:
            entry = dict(row)
            entry["factors"] = json.loads(entry["factors_json"])
            del entry["factors_json"]
            entries.append(entry)
    return entries