from datetime import date, datetime
import json
from pathlib import Path


BIRTHDAYS_FILE = Path("data/birthdays.json")


def days_until(month: int, day: int) -> int:
    today = date.today()
    target = date(today.year, month, day)

    if target < today:
        target = date(today.year + 1, month, day)

    return (target - today).days


def load_birthdays():
    if not BIRTHDAYS_FILE.exists():
        return []

    with open(BIRTHDAYS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_birthdays():
    items = []

    for item in load_birthdays():
        try:
            birthday_date = datetime.strptime(item["date"], "%m-%d")
            delta = days_until(birthday_date.month, birthday_date.day)

            items.append({
                "name": item.get("name", "Unknown"),
                "date": item["date"],
                "note": item.get("note", ""),
                "days_until": delta,
            })
        except Exception as error:
            items.append({
                "name": item.get("name", "Invalid"),
                "date": item.get("date"),
                "note": item.get("note", ""),
                "error": str(error),
            })

    return {
        "source": "local",
        "items": sorted(
            items,
            key=lambda item: item.get("days_until", 9999),
        ),
    }
