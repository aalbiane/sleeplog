from datetime import datetime

def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_time(time_str):
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False

def validate_rating(value, min_val=1, max_val=10):
    try:
        v = int(value)
        return min_val <= v <= max_val
    except ValueError:
        return False