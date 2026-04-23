from datetime import datetime, timedelta
from collections import Counter
import json

def calculate_sleep_hours(bedtime, wakeup_time, date_str):
    """Замыкания нет, но чистая функция для расчёта часов сна"""
    bed = datetime.strptime(f"{date_str} {bedtime}", "%Y-%m-%d %H:%M")
    wake = datetime.strptime(f"{date_str} {wakeup_time}", "%Y-%m-%d %H:%M")
    if wake <= bed:
        wake += timedelta(days=1)
    delta = wake - bed
    return round(delta.total_seconds() / 3600, 2)

def get_average_metrics(entries):
    """Средние показатели"""
    if not entries:
        return 0, 0, 0
    total_hours = sum(e["sleep_hours"] for e in entries)
    total_quality = sum(e["sleep_quality"] for e in entries)
    total_energy = sum(e["morning_energy"] for e in entries)
    n = len(entries)
    return total_hours / n, total_quality / n, total_energy / n

def get_most_frequent_factors(entries):
    """Наиболее частые факторы (положительные/отрицательные)"""
    all_factors = [factor for entry in entries for factor in entry["factors"]]
    if not all_factors:
        return [], []
    counter = Counter(all_factors)
    # Условно: факторы со стрессом/кофеином считаем негативными
    negative_keywords = ["стресс", "кофеин", "экраны"]
    positive_keywords = ["тихая обстановка", "сон на улице", "физическая активность"]
    
    positive = [f for f, _ in counter.most_common(3) if any(p in f.lower() for p in positive_keywords)]
    negative = [f for f, _ in counter.most_common(3) if any(n in f.lower() for n in negative_keywords)]
    return positive, negative

def text_visualization(entries, days=7):
    """Текстовая визуализация сна"""
    if not entries:
        return "Нет данных"
    
    lines = []
    days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    for i, entry in enumerate(entries[:days]):
        hours = entry["sleep_hours"]
        full_hours = int(hours)
        minutes = int((hours - full_hours) * 60)
        bar_len = int(hours)
        bar = "█" * min(bar_len, 20)
        lines.append(f"{days_of_week[i]}: {bar} {full_hours}ч {minutes:02d}м")
    return "\n".join(lines)

def create_factor_filter(factor):
    """ЗАМЫКАНИЕ: фабрика фильтров по фактору"""
    def filter_by_factor(entry):
        return factor.lower() in [f.lower() for f in entry["factors"]]
    return filter_by_factor

def generate_insights(entries):
    """Персональные инсайты с использованием filter/map/lambda"""
    insights = []
    
    if len(entries) < 2:
        return ["Недостаточно данных для инсайтов"]
    
    # Инсайт про кофеин (используем filter и lambda)
    has_caffeine = list(filter(lambda e: "кофеин" in [f.lower() for f in e["factors"]], entries))
    no_caffeine = list(filter(lambda e: "кофеин" not in [f.lower() for f in e["factors"]], entries))
    
    if has_caffeine and no_caffeine:
        avg_caffeine = sum(e["sleep_hours"] for e in has_caffeine) / len(has_caffeine)
        avg_no_caffeine = sum(e["sleep_hours"] for e in no_caffeine) / len(no_caffeine)
        diff = avg_no_caffeine - avg_caffeine
        if diff > 0.5:
            h = int(diff)
            m = int((diff - h) * 60)
            insights.append(f"☕ В дни без кофеина вы спите на {h}ч {m:02d}м дольше")
    
    # Инсайт про физическую активность (map для извлечения качества сна)
    active = list(filter(lambda e: "физическая активность" in [f.lower() for f in e["factors"]], entries))
    inactive = list(filter(lambda e: "физическая активность" not in [f.lower() for f in e["factors"]], entries))
    
    if active and inactive:
        quality_active = list(map(lambda e: e["sleep_quality"], active))
        quality_inactive = list(map(lambda e: e["sleep_quality"], inactive))
        avg_active = sum(quality_active) / len(quality_active)
        avg_inactive = sum(quality_inactive) / len(quality_inactive)
        if avg_active > avg_inactive:
            increase = ((avg_active - avg_inactive) / avg_inactive) * 100
            insights.append(f"🏃 Качество сна выше на {increase:.0f}%, когда вы занимаетесь спортом")
    
    # "Глубокие ночи" с filter
    deep_nights = list(filter(lambda e: e["sleep_hours"] >= 7.5, entries))
    if deep_nights:
        avg_quality = sum(e["sleep_quality"] for e in deep_nights) / len(deep_nights)
        insights.append(f"💤 В глубокие ночи (≥7.5ч) качество сна = {avg_quality:.1f}/10")
        # Новый инсайт про качество сна и энергию (добавьте это в функцию generate_insights)
    if len(entries) >= 3:
        high_energy = list(filter(lambda e: e["morning_energy"] >= 8, entries))
        low_energy = list(filter(lambda e: e["morning_energy"] <= 4, entries))
        
        if high_energy and low_energy:
            avg_quality_high = sum(e["sleep_quality"] for e in high_energy) / len(high_energy)
            avg_quality_low = sum(e["sleep_quality"] for e in low_energy) / len(low_energy)
            if avg_quality_high > avg_quality_low:
                diff = avg_quality_high - avg_quality_low
                insights.append(f"⚡ Высокая утренняя энергия коррелирует с качеством сна: +{diff:.1f} балла")
    return insights if insights else ["Продолжайте заполнять дневник для персонализированных советов"]