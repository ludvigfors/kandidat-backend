from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
engine = create_engine('sqlite:///images.db', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    coordinates = Column(JSON)
    image_path = Column(String, unique=True)

    def __init__(self, coordinates, image_path):
        self.coordinates = coordinates
        self.image_path = image_path

Base.metadata.create_all(engine)