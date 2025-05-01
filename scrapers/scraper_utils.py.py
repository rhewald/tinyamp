from datetime import datetime

def normalize_date(short_date):
    """
    Convert date in '5.1' format to ISO 8601 'YYYY-MM-DD'.
    Assumes all dates are in current year.
    """
    try:
        month, day = map(int, short_date.strip().split('.'))
        year = datetime.now().year
        return datetime(year, month, day).strftime('%Y-%m-%d')
    except Exception:
        return None

def normalize_time(raw_time):
    """
    Normalize time strings to 'SHOW: H:MM AM/PM' format.
    Supports formats like '20:00' or already formatted 'SHOW: 8:00 PM'.
    """
    if raw_time is None:
        return None
    raw_time = raw_time.strip()
    if raw_time.upper().startswith("SHOW:"):
        return raw_time  # already normalized
    try:
        dt = datetime.strptime(raw_time, "%H:%M")
        return f"SHOW: {dt.strftime('%-I:%M %p')}"  # e.g. 20:00 → SHOW: 8:00 PM
    except Exception:
        return raw_time  # fallback to original if parsing fails
