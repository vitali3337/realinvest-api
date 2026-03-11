def parse_makler():

    url = "https://makler.md/real-estate/real-estate-for-sale"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print("Ошибка загрузки Makler:", e)
        return []

    soup = BeautifulSoup(r.text, "html.parser")

    listings = []

    # Пытаемся найти карточки объявлений
    cards = soup.select("div.advert")

    for card in cards:

        title_el = card.select_one(".title")
        price_el = card.select_one(".price")
        link_el = card.select_one("a")
        img_el = card.select_one("img")

        title = title_el.get_text(strip=True) if title_el else None
        price_text = price_el.get_text(strip=True) if price_el else None
        link = link_el["href"] if link_el and link_el.get("href") else None
        img = img_el["src"] if img_el and img_el.get("src") else None

        if not title or not link:
            continue

        if not link.startswith("http"):
            link = "https://makler.md" + link

        # извлечение цены
        price = 0
        if price_text:
            digits = "".join(c for c in price_text if c.isdigit())
            if digits:
                price = int(digits)

        listing = {
            "title": title,
            "type": "дом",
            "district": "",
            "price": price,
            "area": None,
            "rooms": None,
            "img": img,
            "desc": "",
            "link": link,
            "source": "makler",
            "parsed": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        listings.append(listing)

        if len(listings) >= 30:
            break

    return listings
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

    r = requests.get(url, headers=headers)

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

    data.extend(new_items)

    save_data(data)

    print("Добавлено объявлений:", len(new_items))
