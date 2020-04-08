import os

from string import Formatter

from sqlalchemy import create_engine, event
from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy import Integer, Float, String
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm import composite, relationship
from sqlalchemy.ext.declarative import declarative_base

import sqlite3

from contextlib import contextmanager

from threading import Lock

from helper_functions import get_path_from_root

DATABASE_FILE_PATH = get_path_from_root("/IMM_database/IMM_database.db")


Base = declarative_base()

# This formatter is used to automatically handle formatting of None values.
class NoneFormatter(Formatter):
    def __init__(self, namespace={}):
        super().__init__()
        self.namespace = namespace

    def format_field(self, value, format_spec):
        if value == None:
            return "NULL"
        else:
            return super().format_field(value, format_spec)


# This class is inspired by the SQLAlchemy tutorial.
# https://docs.sqlalchemy.org/en/13/orm/composites.html
class Coordinate:
    def __init__(self, lat, long):
        self.lat = lat
        self.long = long
    
    def __composite_values__(self):
        return self.lat, self.long

    def __repr__(self):
        return NoneFormatter().format("Coordinate(lat={}, long={})", self.lat, self.long)

    def __eq__(self, other):
        return isinstance(other, Coordinate) and self.lat == other.lat and self.long == other.long

    def __ne__(self, other):
        return not self.__eq__(other)


class UserSession(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    start_time = Column(Integer, nullable=False)
    end_time = Column(Integer)
    drone_mode = Column(String, nullable=False)

    def __repr__(self):
        return NoneFormatter().format('<UserSession(id={:6d}, start_time={}, end_time={}, drone_mode={}', 
            self.id, self.start_time, self.end_time, self.drone_mode)


class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    __up_left_lat = Column(Float, nullable=False)
    __up_left_long = Column(Float, nullable=False)
    __up_right_lat = Column(Float, nullable=False)
    __up_right_long = Column(Float, nullable=False)
    __down_right_lat = Column(Float, nullable=False)
    __down_right_long = Column(Float, nullable=False)
    __down_left_lat = Column(Float, nullable=False)
    __down_left_long = Column(Float, nullable=False)

    up_left = composite(Coordinate, __up_left_lat, __up_left_long)
    up_right = composite(Coordinate, __up_right_lat, __up_right_long)
    down_right = composite(Coordinate, __down_right_lat, __down_right_long)
    down_left = composite(Coordinate, __down_left_lat, __down_left_long)

    session = relationship("UserSession", back_populates="clients")

    def __repr__(self):
        return NoneFormatter().format('<Client(id={0:6d}, session_id={1:6d}, up_left={2}, up_right={3}, down_right={4}, down_left={5}',
            self.id, self.session_id, self.up_left, self.up_right, self.down_right, self.down_left)


UserSession.clients = relationship("Client", order_by=Client.id, back_populates="session")


class AreaVertex(Base):
    __tablename__ = 'areas'

    session_id = Column(Integer, ForeignKey('sessions.id'), primary_key=True)
    vertex_no = Column(Integer, primary_key=True, nullable=False)
    __coordinate_lat = Column(Float, nullable=False)
    __coordinate_long = Column(Float, nullable=False)
    
    coordinate = composite(Coordinate, __coordinate_lat, __coordinate_long)

    session = relationship("UserSession", back_populates="area_vertices")

    def __repr__(self):
        return NoneFormatter().format('<AreaVertex(session_id={0:6d}, vertex_no={1:6d}, coordinate={2}',
            self.session_id, self.vertex_no, self.coordinate.__repr__())


UserSession.area_vertices = relationship("AreaVertex", order_by=AreaVertex.vertex_no, back_populates="session")


class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    time_taken = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    __up_left_lat = Column(Float, nullable=False)
    __up_left_long = Column(Float, nullable=False)
    __up_right_lat = Column(Float, nullable=False)
    __up_right_long = Column(Float, nullable=False)
    __down_right_lat = Column(Float, nullable=False)
    __down_right_long = Column(Float, nullable=False)
    __down_left_lat = Column(Float, nullable=False)
    __down_left_long = Column(Float, nullable=False)
    __center_lat = Column(Float, nullable=False)
    __center_long = Column(Float, nullable=False)
    file_name = Column(String, nullable=False)

    up_left = composite(Coordinate, __up_left_lat, __up_left_long)
    up_right = composite(Coordinate, __up_right_lat, __up_right_long)
    down_right = composite(Coordinate, __down_right_lat, __down_right_long)
    down_left = composite(Coordinate, __down_left_lat, __down_left_long)
    center = composite(Coordinate, __center_lat, __center_long)

    session = relationship("UserSession", back_populates="images")

    def __repr__(self):
        return NoneFormatter().format('<Image(id={:6d}, session_id={:6d}, time_taken={}, width={:4d}px, height={:4d}px, type={}, up_left={}, up_right={}, down_right={}, down_left={}, file_path={}',
            self.id, self.session_id, self.time_taken, self.width, self.height, self.type, self.up_left.__repr__(), self.up_right.__repr__(), self.down_right.__repr__(), self.down_left.__repr__(), self.file_name)


UserSession.images = relationship("Image", order_by=Image.id, back_populates="session")


class PrioImage(Base):
    __tablename__ = 'prio_images'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    time_requested = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    image_id = Column(Integer, ForeignKey('images.id'), nullable=True)
    eta = Column(Integer, nullable=True)
    __coordinate_lat = Column(Float, nullable=False)
    __coordinate_long = Column(Float, nullable=False)
    
    coordinate = composite(Coordinate, __coordinate_lat, __coordinate_long)
    
    session = relationship("UserSession", back_populates="prio_images")
    image = relationship("Image", uselist=False, back_populates="prio_image")

    def __repr__(self):
        return NoneFormatter().format('<PrioImage(id={0:6d}, session_id={1:6d}, time_requested={2}, coordinate={3}, status={4}, image_id={5:6d}, eta={6}',
            self.id, self.session_id, self.time_requested, self.coordinate.__repr__(), self.status, self.image_id, self.eta)


UserSession.prio_images = relationship("PrioImage", order_by=PrioImage.id, back_populates="session")
Image.prio_image = relationship("PrioImage", order_by=PrioImage.id, uselist=False, back_populates="image")


class Drone(Base):
    __tablename__ = 'drones'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    last_updated = Column(Integer, nullable=True)
    eta = Column(Integer, nullable=True)

    session = relationship("UserSession", back_populates="drones")

    def __repr__(self):
        return NoneFormatter().format('<Drone(id={0:6d}, session_id={1:6d}, last_updated={2}, eta={3}',
            self.id, self.session_id, self.last_updated, self.eta)


UserSession.drones = relationship("Drone", order_by=Drone.id, back_populates="session")

# This is required to enable foreign key constraints in SQLite, see:
# https://www.scrygroup.com/tutorial/2018-05-07/SQLite-foreign-keys/
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

class Database:
    def __init__(self, file_path, echo=False):
        self.__engine = create_engine('sqlite:///' + file_path, echo=echo)
        Base.metadata.create_all(bind=self.__engine)
        self.__session_maker = sessionmaker(bind=self.__engine)
        self.__Session = scoped_session(self.__session_maker)

    def get_session(self):
        return self.__Session()

    def release_session(self):
        return self.__Session.remove()


__active_databases = {}
__active_database_mutex = Lock()

def __get_database_instance(file_path):
    # This is a critical section, as multiple instances of the same Database
    # might be created by different threads.
    __active_database_mutex.acquire()
    if not file_path in __active_databases.keys():
        __active_databases[file_path] = Database(file_path)
    __active_database_mutex.release()
    return __active_databases[file_path]

def get_database():
    return __get_database_instance(DATABASE_FILE_PATH)

def get_test_database(in_memory=True):
    if in_memory:
        return Database(":memory:")
    else:
        if os.path.exists("test.db"):
            os.remove("test.db")
        return __get_database_instance("test.db")

# This context manager is inspired by the sqlalchemy session tutorial.
# https://docs.sqlalchemy.org/en/13/orm/session_basics.html
@contextmanager
def session_scope():
    db = get_database()
    session = db.get_session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
        db.release_session()

if __name__ == '__main__':
    with session_scope() as session:
        # The session only exists withing this with statement. Commit, rollback
        # and release are performed automatically by the context manager when
        # appropriate.
        for user_session in session.query(UserSession).all():
            print(user_session)