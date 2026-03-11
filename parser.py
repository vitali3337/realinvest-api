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
    url = "https://makler.md/real-estate"
    
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    listings = []

    for item in soup.select("a")[:10]:
        title = item.get_text(strip=True)

        if len(title) > 20:
            listings.append({
                "title": title,
                "type": "дом",
                "district": "",
                "price": 0,
                "area": None,
                "rooms": None,
                "desc": "",
                "source": "makler",
                "parsed": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

    return listings


def run():
    data = load_data()

    new_items = parse_makler()

    data.extend(new_items)

    save_data(data)

    print("Добавлено объявлений:", len(new_items))


if __name__ == "__main__":
    run()
