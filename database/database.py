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
        return '<UserSession(id={0:6d}, start_time={1}, end_time={2}, drone_mode={3}'.format(self.id, self.start_time, self.end_time, self.drone_mode)


class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    coordinates = Column(Float)

    session = relationship("UserSession", back_populates="clients")

UserSession.clients = relationship("Client", order_by=Client.id, back_populates="session")


class AreaVertex(Base):
    __tablename__ = 'areas'

    session_id = Column(Integer, ForeignKey('sessions.id'), primary_key=True)
    vertex_no = Column(Integer, primary_key=True)
    coordinate = Column(Float, nullable=False)

    session = relationship("UserSession", back_populates="area_vertices")

UserSession.area_vertices = relationship("AreaVertex", order_by=AreaVertex.vertex_no, back_populates="session")


class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    sesssion_id = Column(Integer, ForeignKey('sessions.id'))
    time_taken = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    coordinates = Column(Float, nullable=False)
    file_name = Column(String, nullable=False)

    session = relationship("UserSession", back_populates="images")

UserSession.images = relationship("Image", order_by=Image.id, back_populates="session")


class PrioImage(Base):
    __tablename__ = 'prio_images'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    time_requested = Column(Integer, nullable=False)
    coordinate = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    image = Column(Integer, ForeignKey('images.id'), nullable=True)
    eta = Column(Integer, nullable=True)

    session = relationship("UserSession", back_populates="prio_images")

UserSession.prio_images = relationship("PrioImage", order_by=PrioImage.id, back_populates="session")


class Drone(Base):
    __tablename__ = 'drones'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    last_updated = Column(Integer, nullable=True)
    eta = Column(Integer, nullable=True)

    session = relationship("UserSession", back_populates="drones")

UserSession.drones = relationship("Drone", order_by=PrioImage.id, back_populates="session")

engine = create_engine('sqlite:///' + DATABASE_FILE_NAME, echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

if __name__ == '__main__':
    session = Session()

    sample_session = UserSession(start_time=123, drone_mode='AUTO')
    session.add(sample_session)
    session.commit()

    all_sessions = session.query(UserSession).all()
    for session in all_sessions:
        print(session)