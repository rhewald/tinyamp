import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient

# Load the environment variables from server/.env
load_dotenv(dotenv_path="server/.env")


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
        time_str = raw_time.replace("SHOW:", "").strip().upper()
        if ":" in time_str and len(time_str) <= 5 and time_str[0].isdigit():
            hour, minute = map(int, time_str.split(":"))
            t = datetime.strptime(f"{hour}:{minute}", "%H:%M")
            return f"SHOW: {t.strftime('%-I:%M %p')}"
        return f"SHOW: {time_str}"
    except:
        return raw_time


def insert_unique_events(events, db_name="tinyamp", collection_name="events", uri=None):
    if not uri:
        uri = os.getenv("MONGO_URI")

    if not uri:
        print("❌ MONGO_URI not set. Check your server/.env file.")
        return

    client = MongoClient(uri)
    db = client["tinyamp"]
    collection = db[collection_name]

    inserted = 0
    skipped = 0

    for event in events:
        if not event.get("artist") or not event.get("date") or not event.get("venue"):
            print("⚠️ Skipping event due to missing artist, date, or venue:", event)
            continue

        query = {
            "artist": event["artist"],
            "date": event["date"],
            "venue": event["venue"]
        }

        if collection.find_one(query):
            print(f"⏭️ Duplicate found, skipping: {event['artist']} @ {event['venue']} on {event['date']}")
            skipped += 1
        else:
            collection.insert_one(event)
            print(f"✅ Inserted: {event['artist']} @ {event['venue']} on {event['date']}")
            inserted += 1

    print(f"\nDone. Inserted: {inserted}, Skipped (duplicates): {skipped}")
    client.close()
