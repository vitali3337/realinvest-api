from sqlalchemy import Column, Integer, String, Text
from database import Base

class Listing(Base):

    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String)
    price = Column(Integer)
    city = Column(String)

    rooms = Column(Integer)
    floor = Column(String)

    phone = Column(String)
    description = Column(Text)

    image = Column(String)

    image2 = Column(String)
    image3 = Column(String)
    image4 = Column(String)
    image5 = Column(String)
    image6 = Column(String)
    image7 = Column(String)
    image8 = Column(String)
    image9 = Column(String)
    image10 = Column(String)
