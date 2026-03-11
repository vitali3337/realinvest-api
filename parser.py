import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

DATA_FILE = "houses.json"


def load_data():
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def parse_makler():

    url = "https://makler.md/real-estate/real-estate-for-sale"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
    except:
        print("Ошибка подключения к Makler")
        return []

    soup = BeautifulSoup(r.text, "html.parser")

    listings = []

    cards = soup.select("a")

    for card in cards:

        title = card.get_text(strip=True)

        if len(title) < 25:
            continue

        link = card.get("href")

        if link and not link.startswith("http"):
            link = "https://makler.md" + link

        listing = {
            "title": title,
            "type": "дом",
            "district": "",
            "price": 0,
            "area": None,
            "rooms": None,
            "img": None,
            "desc": "",
            "link": link,
            "source": "makler",
            "parsed": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        listings.append(listing)

        if len(listings) >= 20:
            break

    return listings


def run():

    data = load_data()

    new_items = parse_makler()

    existing_links = {item.get("link") for item in data}

    added = 0

    for item in new_items:
        if item.get("link") not in existing_links:
            data.append(item)
            added += 1

    save_data(data)

    print("Добавлено объявлений:", added)


if __name__ == "__main__":
    run()
