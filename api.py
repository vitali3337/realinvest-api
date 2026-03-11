from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import estate_parser

app = FastAPI()

DATA_FILE = "houses.json"


# -----------------------------
# CORS (для фронтенда сайта)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# загрузка объявлений
# -----------------------------
def load_data():
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


# -----------------------------
# главная страница
# -----------------------------
@app.get("/")
def root():
    return {"status": "RealInvest API working"}


# -----------------------------
# список объявлений
# -----------------------------
@app.get("/listings")
def get_listings(
    city: str = None,
    district: str = None,
    min_price: int = None,
    max_price: int = None,
    limit: int = 50,
    offset: int = 0
):

    data = load_data()

    results = []

    for item in data:

        if city and city.lower() not in item.get("title", "").lower():
            continue

        if district and district.lower() not in item.get("district", "").lower():
            continue

        price = item.get("price", 0)

        if min_price and price < min_price:
            continue

        if max_price and price > max_price:
            continue

        results.append(item)

    total = len(results)

    results = results[offset: offset + limit]

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "listings": results
    }


# -----------------------------
# статистика портала
# -----------------------------
@app.get("/stats")
def get_stats():

    data = load_data()

    sources = {}

    for item in data:
        src = item.get("source", "unknown")
        sources[src] = sources.get(src, 0) + 1

    return {
        "total_listings": len(data),
        "sources": sources
    }


# -----------------------------
# запуск парсера
# -----------------------------
@app.get("/run-parser")
def run_parser():

    estate_parser.run()

    return {
        "status": "parser executed"
    }
