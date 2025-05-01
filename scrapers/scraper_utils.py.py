from datetime import datetime

def normalize_date(short_date):
    """
    Converts short dates like '5.1' into full ISO format '2025-05-01'.
    Assumes all dates are in the current calendar year.
    """
    try:
        month, day = map(int, short_date.strip().split('.'))
        year = datetime.now().year
        return datetime(year=year, month=month, day=day).strftime("%Y-%m-%d")
    except Exception:
        return None

def normalize_time(raw_time):
    """
    Normalizes times to US-style format: 'SHOW: 8:00 PM'.
    Accepts input like '20:00' or already-formatted values.
    """
    try:
        raw_time = raw_time.replace("SHOW:", "").strip()
        dt_obj = datetime.strptime(raw_time, "%H:%M")
        return "SHOW: " + dt_obj.strftime("%-I:%M %p")
    except ValueError:
        # If already formatted (e.g., 'SHOW: 8:00 PM'), return as-is
        return raw_time if "SHOW:" in raw_time else f"SHOW: {raw_time}"
