from sqlalchemy import create_engine
from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy import Integer, Float, String

from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base

file_name = "database/database.db"

Base = declarative_base()

class UserSession(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    start_time = Column(Integer, nullable=False)
    end_time = Column(Integer)
    drone_mode = Column(String, nullable=False)


class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    session = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    coordinates = Column(Float)


class AreaVertex(Base):
    __tablename__ = 'areas'

    session = Column(Integer, ForeignKey('sessions.id'), primary_key=True)
    vertex_no = Column(Integer, primary_key=True)
    coordinate = Column(Float, nullable=False)


class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    sesssion = Column(Integer, ForeignKey('sessions.id'))
    time_taken = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    coordinates = Column(Float, nullable=False)
    file_name = Column(String, nullable=False)


class PrioImage(Base):
    __tablename__ = 'prio_images'

    id = Column(Integer, primary_key=True)
    session = Column(Integer, ForeignKey('sessions.id'))
    time_requested = Column(Integer, nullable=False)
    coordinate = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    image = Column(Integer, ForeignKey('images.id'), nullable=True)
    eta = Column(Integer, nullable=True)


class Drone(Base):
    __tablename__ = 'drones'

    id = Column(Integer, primary_key=True)
    session = Column(Integer, ForeignKey('sessions.id'))
    last_updated = Column(Integer, nullable=True)
    eta = Column(Integer, nullable=True)


if __name__ == '__main__':
    engine = create_engine('sqlite:///' + file_name, echo=True)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()

    sample_session = UserSession(start_time=123, drone_mode='AUTO')
    session.add(sample_session)
    session.commit()