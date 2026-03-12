from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    price = Column(Integer)
    city = Column(String)
    rooms = Column(Integer)
    floor = Column(String)
    phone = Column(String)
    description = Column(String)
    image = Column(String)
