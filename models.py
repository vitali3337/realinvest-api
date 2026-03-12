from sqlalchemy import Column, Integer, String
from database import Base

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String)
    price = Column(Integer)
    city = Column(String)
    rooms = Column(String)
    floor = Column(String)
    phone = Column(String)
    description = Column(String)
    image = Column(String)
