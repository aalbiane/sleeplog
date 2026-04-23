import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import init_db, save_entry, get_entry, get_entries_for_period, get_all_entries
from src.validators import validate_date, validate_time, validate_rating
from src.analytics import (calculate_sleep_hours, get_average_metrics, 
                           get_most_frequent_factors, text_visualization,
                           generate_insights, create_factor_filter)
from src.file_handlers import export_full_zip, import_from_zip, backup_database
from src.config import get_logger
from datetime import datetime, timedelta

logger = get_logger()

AVAILABLE_FACTORS = [
    "кофеин", "экраны перед сном", "физическая активность",
    "стресс", "тихая обстановка", "сон на улице"
]

def input_factors():
    """Ввод факторов (множественный выбор)"""
    print("\nДоступные факторы:")
    for i, f in enumerate(AVAILABLE_FACTORS, 1):
        print(f"{i}. {f}")
    print("0. Свой вариант")
    
    selected = []
    while True:
        choice = input("Введите номер фактора (или 'q' для завершения): ").strip()
        if choice.lower() == 'q':
            break
        if choice == '0':
            custom = input("Введите свой фактор: ").strip()
            if custom:
                selected.append(custom)
        elif choice.isdigit() and 1 <= int(choice) <= len(AVAILABLE_FACTORS):
            selected.append(AVAILABLE_FACTORS[int(choice)-1])
        else:
            print("Неверный ввод")
    return selected

def add_or_edit_entry():
    """Добавление или редактирование записи"""
    print("\n=== Новая запись сна ===")
    
    date_str = input("Дата (YYYY-MM-DD): ").strip()
    while not validate_date(date_str):
        print("Неверный формат даты")
        date_str = input("Дата (YYYY-MM-DD): ").strip()
    
    existing = get_entry(date_str)
    if existing:
        print(f"\nЗапись за {date_str} уже существует. Будет выполнено редактирование.")
    
    bedtime = input("Время отхода ко сну (HH:MM): ").strip()
    while not validate_time(bedtime):
        print("Неверный формат времени")
        bedtime = input("Время отхода ко сну (HH:MM): ").strip()
    
    wakeup = input("Время пробуждения (HH:MM): ").strip()
    while not validate_time(wakeup):
        print("Неверный формат времени")
        wakeup = input("Время пробуждения (HH:MM): ").strip()
    
    sleep_hours = calculate_sleep_hours(bedtime, wakeup, date_str)
    print(f"Рассчитанная продолжительность сна: {sleep_hours:.2f} часов")
    
    quality = input("Качество сна (1-10): ").strip()
    while not validate_rating(quality):
        quality = input("Качество сна (1-10): ").strip()
    
    energy = input("Уровень энергии утром (1-10): ").strip()
    while not validate_rating(energy):
        energy = input("Уровень энергии утром (1-10): ").strip()
    
    factors = input_factors()
    notes = input("Заметки (опционально): ").strip()
    
    entry = {
        "date": date_str,
        "bedtime": bedtime,
        "wakeup_time": wakeup,
        "sleep_hours": sleep_hours,
        "sleep_quality": int(quality),
        "morning_energy": int(energy),
        "factors": factors,
        "notes": notes
    }
    
    save_entry(entry)
    print(f"✓ Запись за {date_str} сохранена!")

def show_analytics():
    """Показ аналитики"""
    print("\n=== Аналитика сна ===")
    period = input("Показать за (week/month): ").strip().lower()
    
    today = datetime.now().date()
    if period == "week":
        start_date = (today - timedelta(days=7)).isoformat()
        end_date = today.isoformat()
    elif period == "month":
        start_date = (today - timedelta(days=30)).isoformat()
        end_date = today.isoformat()
    else:
        print("Неверный период")
        return
    
    entries = get_entries_for_period(start_date, end_date)
    if not entries:
        print("Нет данных за выбранный период")
        return
    
    avg_hours, avg_quality, avg_energy = get_average_metrics(entries)
    print(f"\n📊 Сводка за период:")
    print(f"  Средняя продолжительность сна: {avg_hours:.2f} ч")
    print(f"  Среднее качество сна: {avg_quality:.1f}/10")
    print(f"  Средняя утренняя энергия: {avg_energy:.1f}/10")
    
    pos_factors, neg_factors = get_most_frequent_factors(entries)
    if pos_factors:
        print(f"  Частые позитивные факторы: {', '.join(pos_factors)}")
    if neg_factors:
        print(f"  Частые негативные факторы: {', '.join(neg_factors)}")
    
    print("\n📈 Текстовая визуализация сна:")
    print(text_visualization(entries))
    
    print("\n💡 Персональные инсайты:")
    insights = generate_insights(entries)
    for insight in insights:
        print(f"  • {insight}")
    
    # Пример использования замыкания
    print("\n🔍 Проверка замыкания (фильтр по фактору 'стресс'):")
    stress_filter = create_factor_filter("стресс")
    stressful_days = list(filter(stress_filter, entries))
    if stressful_days:
        print(f"  Дней со стрессом: {len(stressful_days)}")
    else:
        print("  Дней со стрессом не найдено")

def main_menu():
    init_db()
    while True:
        print("\n" + "="*50)
        print("💤 SleepLog - Журнал сна и биоритмов")
        print("="*50)
        print("1. Добавить/редактировать запись о сне")
        print("2. Показать аналитику")
        print("3. Экспорт всех данных в ZIP")
        print("4. Импорт данных из ZIP")
        print("5. Создать резервную копию БД")
        print("0. Выход")
        
        choice = input("\nВыберите действие: ").strip()
        
        if choice == "1":
            add_or_edit_entry()
        elif choice == "2":
            show_analytics()
        elif choice == "3":
            entries = get_all_entries()
            if not entries:
                print("Нет данных для экспорта")
                continue
            filename = input("Имя ZIP-файла (по умолчанию sleep_export.zip): ").strip()
            if not filename:
                filename = "sleep_export.zip"
            export_full_zip(entries, filename)
            print(f"✓ Данные экспортированы в {filename}")
        elif choice == "4":
            zip_path = input("Путь к ZIP-файлу для импорта: ").strip()
            try:
                import_from_zip(zip_path)
                print("✓ Импорт выполнен успешно")
            except Exception as e:
                print(f"Ошибка импорта: {e}")
                logger.error(f"Ошибка импорта: {e}")
        elif choice == "5":
            backup_path = backup_database()
            print(f"✓ Бэкап создан: {backup_path}")
        elif choice == "0":
            print("До свидания! Хорошего сна!")
            break
        else:
            print("Неверный выбор")

if __name__ == "__main__":
    main_menu()