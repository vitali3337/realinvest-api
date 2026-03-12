from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import engine, SessionLocal
from models import Base, Listing

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# модель API
class ListingCreate(BaseModel):
    title: str
    price: int
    city: str
    rooms: int
    floor: str
    phone: str
    description: str
    image: str


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/listings")
def get_listings():

    db = SessionLocal()

    listings = db.query(Listing).all()

    result = []

    for l in listings:
        result.append({
            "id": l.id,
            "title": l.title,
            "price": l.price,
            "city": l.city,
            "rooms": l.rooms,
            "floor": l.floor,
            "phone": l.phone,
            "description": l.description,
            "image": l.image
        })

    db.close()

    return {
        "total": len(result),
        "listings": result
    }


@app.post("/listings")
def add_listing(listing: ListingCreate):

    db = SessionLocal()

    new_listing = Listing(
        title=listing.title,
        price=listing.price,
        city=listing.city,
        rooms=listing.rooms,
        floor=listing.floor,
        phone=listing.phone,
        description=listing.description,
        image=listing.image
    )

    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)

    db.close()

    return {"status": "listing added"}
