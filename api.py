from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, Listing

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/listings")
def get_listings(db: Session = Depends(get_db)):
    listings = db.query(Listing).all()

    return {
        "total": len(listings),
        "listings": listings
    }


@app.post("/listings")
def add_listing(data: dict, db: Session = Depends(get_db)):

    listing = Listing(**data)

    db.add(listing)
    db.commit()
    db.refresh(listing)

    return listing


@app.delete("/listings/{id}")
def delete_listing(id: int, db: Session = Depends(get_db)):

    listing = db.query(Listing).get(id)

    db.delete(listing)
    db.commit()

    return {"status":"deleted"}


@app.put("/listings/{id}")
def update_listing(id: int, data: dict, db: Session = Depends(get_db)):

    listing = db.query(Listing).get(id)

    for key in data:
        setattr(listing, key, data[key])

    db.commit()

    return listing
