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


def save_birthdays(items: list):
    BIRTHDAYS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(BIRTHDAYS_FILE, "w", encoding="utf-8") as file:
        json.dump(items, file, ensure_ascii=False, indent=4)


def validate_birthday(name: str, date_str: str, note: str) -> tuple[str, str, str]:
    name = (name or "").strip()
    date_str = (date_str or "").strip()
    note = (note or "").strip()

    if not name:
        raise ValueError("Name is required")

    try:
        datetime.strptime(date_str, "%m-%d")
    except ValueError:
        raise ValueError("Date must be in MM-DD format")

    return name, date_str, note


def add_birthday(name: str, date_str: str, note: str = ""):
    name, date_str, note = validate_birthday(name, date_str, note)
    items = load_birthdays()

    if any(item.get("name") == name for item in items):
        raise ValueError(f"Birthday already exists: {name}")

    item = {"name": name, "date": date_str, "note": note}
    items.append(item)
    save_birthdays(items)

    return item


def update_birthday(name: str, new_name: str, new_date: str, new_note: str = ""):
    new_name, new_date, new_note = validate_birthday(new_name, new_date, new_note)
    items = load_birthdays()

    for item in items:
        if item.get("name") != name:
            continue

        item["name"] = new_name
        item["date"] = new_date
        item["note"] = new_note
        save_birthdays(items)
        return item

    raise ValueError(f"Unknown birthday: {name}")


def delete_birthday(name: str):
    items = load_birthdays()
    remaining = [item for item in items if item.get("name") != name]

    if len(remaining) == len(items):
        raise ValueError(f"Unknown birthday: {name}")

    save_birthdays(remaining)


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
