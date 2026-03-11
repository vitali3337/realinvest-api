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
