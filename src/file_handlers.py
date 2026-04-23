import csv
import json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
import sqlite3
from src.config import DB_PATH, get_logger

logger = get_logger()

def backup_database():
    """Автоматический бэкап в папку backups/"""
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"backup_{timestamp}.sqlite"
    shutil.copy2(DB_PATH, backup_path)
    logger.info(f"Создан бэкап: {backup_path}")
    return backup_path

def export_to_csv(entries, filename="sleep_export.csv"):
    """Экспорт в CSV"""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "sleep_hours", "sleep_quality", "morning_energy", "factors"])
        for e in entries:
            writer.writerow([
                e["date"], e["sleep_hours"], e["sleep_quality"],
                e["morning_energy"], ", ".join(e["factors"])
            ])
    logger.info(f"Экспортировано в CSV: {filename}")
    return filename

def export_to_json(entries, filename="sleep_export.json"):
    """Экспорт в JSON (полные записи)"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    logger.info(f"Экспортировано в JSON: {filename}")
    return filename

def export_full_zip(entries, zip_filename="sleep_export.zip"):
    """Экспорт всего: CSV + JSON + копия БД в ZIP"""
    csv_file = export_to_csv(entries, "temp_export.csv")
    json_file = export_to_json(entries, "temp_export.json")
    backup_file = backup_database()
    
    with zipfile.ZipFile(zip_filename, "w") as zf:
        zf.write(csv_file, arcname="sleep_data.csv")
        zf.write(json_file, arcname="sleep_data.json")
        zf.write(backup_file, arcname=backup_file.name)
    
    # Удаляем временные файлы
    Path(csv_file).unlink()
    Path(json_file).unlink()
    logger.info(f"Создан полный экспорт: {zip_filename}")
    return zip_filename

def import_from_zip(zip_path):
    """Импорт из ранее экспортированного ZIP"""
    import tempfile
    import json
    from src.database import save_entry, get_entry
    
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmpdir)
        
        json_path = Path(tmpdir) / "sleep_data.json"
        if not json_path.exists():
            raise FileNotFoundError("В архиве нет файла sleep_data.json")
        
        with open(json_path, "r", encoding="utf-8") as f:
            entries = json.load(f)
        
        for entry in entries:
            # Проверяем, существует ли уже запись
            existing = get_entry(entry["date"])
            if existing:
                logger.info(f"Запись за {entry['date']} уже существует, пропускаем")
                continue
            save_entry(entry)
    
    logger.info(f"Импорт завершён из {zip_path}")