from sqlalchemy import create_engine
from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy import Integer, Float, String

from sqlalchemy.orm import sessionmaker, relationship

from sqlalchemy.ext.declarative import declarative_base

DATABASE_FILE_NAME = "database/database.db"

Base = declarative_base()

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
    coordinates = Column(Float)

    session = relationship("UserSession", back_populates="clients")

    def __repr__(self):
        return '<Client(id={0:6d}, session_id={1:6d}, coordinates={2}'.format(
            self.id, self.session_id, self.coordinates)

UserSession.clients = relationship("Client", order_by=Client.id, back_populates="session")


class AreaVertex(Base):
    __tablename__ = 'areas'

    session_id = Column(Integer, ForeignKey('sessions.id'), primary_key=True)
    vertex_no = Column(Integer, primary_key=True)
    coordinate = Column(Float, nullable=False)

    session = relationship("UserSession", back_populates="area_vertices")

    def __repr__(self):
        return '<AreaVertex(session_id={0:6d}, vertex_no={1:6d}, coordinate={2}'.format(
            self.session_id, self.vertex_no, self.coordinate)

UserSession.area_vertices = relationship("AreaVertex", order_by=AreaVertex.vertex_no, back_populates="session")


class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    time_taken = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    coordinates = Column(Float, nullable=False)
    file_name = Column(String, nullable=False)

    session = relationship("UserSession", back_populates="images")

    def __repr__(self):
        return '<Image(id={0:6d}, session_id={1:6d}, time_taken={2}, width={3:4d}px, height={4:4d}px, type={5}, coordinates={6}, file_name={7}'.format(
            self.id, self.session_id, self.time_taken, self.width, self.height, self.type, self.coordinates, self.file_name)

UserSession.images = relationship("Image", order_by=Image.id, back_populates="session")


class PrioImage(Base):
    __tablename__ = 'prio_images'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    time_requested = Column(Integer, nullable=False)
    coordinate = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    image_id = Column(Integer, ForeignKey('images.id'), nullable=True)
    eta = Column(Integer, nullable=True)

    session = relationship("UserSession", back_populates="prio_images")
    image = relationship("Image", back_populates="prio_image")

    def __repr__(self):
        return '<PrioImage(id={0:6d}, session_id={1:6d}, time_requested={2}, coordinate={3}, status={4}, image_id={5:6d}, eta={6}'.format(
            self.id, self.session_id, self.time_requested, self.coordinate, self.status, self.image_id, self.eta)

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
    def __init__(self, file_name):
        self.engine = create_engine('sqlite:///' + file_name, echo=True)
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)


__active_databases = {}

def __get_database_instance(file_name):
    if not file_name in __active_databases.keys():
        __active_databases[file_name] = Database(file_name)
    return __active_databases[file_name]

def get_database():
    return __get_database_instance(DATABASE_FILE_NAME)

def get_test_database():
    return Database(":memory:")


if __name__ == '__main__':
    database = get_test_database()
    session = database.Session()

    sample_session = UserSession(start_time=123, drone_mode='AUTO')
    session.add(sample_session)
    session.commit()

    for user_session in session.query(UserSession).all():
        print(user_session)