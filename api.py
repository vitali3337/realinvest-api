from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

app = FastAPI()

DATA_FILE = "houses.json"

# разрешаем доступ сайту
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# модель объявления
class Listing(BaseModel):
    title: str
    price: int
    city: str
    rooms: int
    floor: str
    phone: str
    description: str
    image: str


# загрузка данных
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


# сохранение данных
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# проверка API
@app.get("/")
def root():
    data = load_data()
    return {"status": "ok", "listings": len(data)}


# получение объявлений
@app.get("/listings")
def get_listings():
    data = load_data()
    return {
        "total": len(data),
        "listings": data
    }


# добавление объявления
@app.post("/listings")
def add_listing(listing: Listing):

    data = load_data()

    new_listing = listing.dict()

    data.append(new_listing)

    save_data(data)

    return {
        "status": "listing added",
        "listing": new_listing
}
