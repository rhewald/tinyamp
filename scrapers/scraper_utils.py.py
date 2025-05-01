from datetime import datetime

def normalize_date(short_date):
    """
    Convert short-form dates like '5.1' to full ISO format like '2025-05-01'.
    Assumes all dates are for the current year and do not wrap into next year.
    """
    try:
        month, day = map(int, short_date.strip().split('.'))
        year = datetime.now().year
        return datetime(year=year, month=month, day=day).strftime("%Y-%m-%d")
    except:
        return None

def normalize_time(raw_time):
    """
    Normalize 24-hour time like '20:00' or already formatted strings to 'SHOW: 8:00 PM'.
    """
    try:
        # Remove prefix if already present
        time_str = raw_time.replace("SHOW:", "").strip().upper()
        # Handle if time is in HH:MM (24-hour)
        if ":" in time_str and len(time_str) <= 5 and time_str[0].isdigit():
            hour, minute = map(int, time_str.split(":"))
            t = datetime.strptime(f"{hour}:{minute}", "%H:%M")
            return f"SHOW: {t.strftime('%-I:%M %p')}"
        # Else, return as-is with proper prefix
        return f"SHOW: {time_str}"
    except:
        return raw_time
