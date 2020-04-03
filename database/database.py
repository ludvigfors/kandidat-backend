from sqlalchemy import create_engine
from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy import Integer, Float, String

from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm import composite, relationship

from sqlalchemy.ext.declarative import declarative_base

from threading import Lock

DATABASE_FILE_PATH = "database/database.db"

Base = declarative_base()

# This class is inspired by the SQLAlchemy tutorial.
# https://docs.sqlalchemy.org/en/13/orm/composites.html
class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __composite_values__(self):
        return self.x, self.y

    def __repr__(self):
        return "Coordinate(x={}, y={})".format(self.x, self.y)

    def __eq__(self, other):
        return isinstance(other, Coordinate) and self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)


class UserSession(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    start_time = Column(Integer, nullable=False)
    end_time = Column(Integer)
    drone_mode = Column(String, nullable=False)

    def __repr__(self):
        return '<UserSession(id={0:6d}, start_time={1}, end_time={2}, drone_mode={3}'.format(
            self.id, self.start_time, self.end_time, self.drone_mode)


class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    __up_left_x = Column(Float, nullable=False)
    __up_left_y = Column(Float, nullable=False)
    __up_right_x = Column(Float, nullable=False)
    __up_right_y = Column(Float, nullable=False)
    __down_right_x = Column(Float, nullable=False)
    __down_right_y = Column(Float, nullable=False)
    __down_left_x = Column(Float, nullable=False)
    __down_left_y = Column(Float, nullable=False)

    up_left = composite(Coordinate, __up_left_x, __up_left_y)
    up_right = composite(Coordinate, __up_right_x, __up_right_y)
    down_right = composite(Coordinate, __down_right_x, __down_right_y)
    down_left = composite(Coordinate, __down_left_x, __down_left_y)

    session = relationship("UserSession", back_populates="clients")

    def __repr__(self):
        return '<Client(id={0:6d}, session_id={1:6d}, coordinates={2}'.format(
            self.id, self.session_id, self.coordinates)


UserSession.clients = relationship("Client", order_by=Client.id, back_populates="session")


class AreaVertex(Base):
    __tablename__ = 'areas'

    session_id = Column(Integer, ForeignKey('sessions.id'), primary_key=True)
    vertex_no = Column(Integer, primary_key=True)
    __coordinate_x = Column(Float, nullable=False)
    __coordinate_y = Column(Float, nullable=False)
    
    coordinate = composite(Coordinate, __coordinate_x, __coordinate_y)

    session = relationship("UserSession", back_populates="area_vertices")

    def __repr__(self):
        return '<AreaVertex(session_id={0:6d}, vertex_no={1:6d}, coordinate={2}'.format(
            self.session_id, self.vertex_no, self.coordinate.__repr__())


UserSession.area_vertices = relationship("AreaVertex", order_by=AreaVertex.vertex_no, back_populates="session")


class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    time_taken = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    __up_left_x = Column(Float, nullable=False)
    __up_left_y = Column(Float, nullable=False)
    __up_right_x = Column(Float, nullable=False)
    __up_right_y = Column(Float, nullable=False)
    __down_right_x = Column(Float, nullable=False)
    __down_right_y = Column(Float, nullable=False)
    __down_left_x = Column(Float, nullable=False)
    __down_left_y = Column(Float, nullable=False)

    up_left = composite(Coordinate, __up_left_x, __up_left_y)
    up_right = composite(Coordinate, __up_right_x, __up_right_y)
    down_right = composite(Coordinate, __down_right_x, __down_right_y)
    down_left = composite(Coordinate, __down_left_x, __down_left_y)
    file_path = Column(String, nullable=False)

    session = relationship("UserSession", back_populates="images")

    def __repr__(self):
        return '<Image(id={0:6d}, session_id={1:6d}, time_taken={2}, width={3:4d}px, height={4:4d}px, type={5}, up_left={6}, up_right={}, down_right={}, down_left={}, file_path={}'.format(
            self.id, self.session_id, self.time_taken, self.width, self.height, self.type, self.up_left.__repr__(), self.up_right.__repr__(), self.down_right.__repr__(), self.down_left.__repr__(), self.file_path)


UserSession.images = relationship("Image", order_by=Image.id, back_populates="session")


class PrioImage(Base):
    __tablename__ = 'prio_images'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    time_requested = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    image_id = Column(Integer, ForeignKey('images.id'), nullable=True)
    eta = Column(Integer, nullable=True)
    __coordinate_x = Column(Float, nullable=False)
    __coordinate_y = Column(Float, nullable=False)
    
    coordinate = composite(Coordinate, __coordinate_x, __coordinate_y)
    
    session = relationship("UserSession", back_populates="prio_images")
    image = relationship("Image", back_populates="prio_image")

    def __repr__(self):
        return '<PrioImage(id={0:6d}, session_id={1:6d}, time_requested={2}, coordinate={3}, status={4}, image_id={5:6d}, eta={6}'.format(
            self.id, self.session_id, self.time_requested, self.coordinate.__repr__(), self.status, self.image_id, self.eta)


UserSession.prio_images = relationship("PrioImage", order_by=PrioImage.id, back_populates="session")
Image.prio_image = relationship("PrioImage", order_by=PrioImage.id, back_populates="image")


class Drone(Base):
    __tablename__ = 'drones'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    last_updated = Column(Integer, nullable=True)
    eta = Column(Integer, nullable=True)

    session = relationship("UserSession", back_populates="drones")


UserSession.drones = relationship("Drone", order_by=PrioImage.id, back_populates="session")


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


def get_test_database():
    return Database(":memory:")


if __name__ == '__main__':
    database = get_test_database()
    session = database.get_session()

    sample_session = UserSession(start_time=123, drone_mode='AUTO')
    session.add(sample_session)
    session.commit()

    for user_session in session.query(UserSession).all():
        print(user_session)

    database.release_session()