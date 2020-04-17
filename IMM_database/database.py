"""Implement functions and classes relating to the IMM database.

The SQLalchemy ORM is used throughout, see https://docs.sqlalchemy.org/en/13/.

The following public ORM classes are provided:
Coordinate -- Column composite class representing a coordinate.
UserSession -- A situation where the IMM is used.
Client -- A user accessing the IMM.
AreaVertex -- Used to track the designated area of a session.
Image -- An image taken by a drone.
PrioImage -- Request from a client to take an image of an area.
Drone -- Information about an RDS drone.

The following public functions are provided:
use_production_db -- Sets the production database as the active database.
use_test_database -- Sets a new test database as the active database.
session_scope -- Context manager to safely interact with database sessions.
"""
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

from threading import Lock, Semaphore

from helper_functions import get_path_from_root

__PRODUCTION_DATABASE_FILE_PATH = get_path_from_root("/IMM_database/IMM_database.db")
__TEST_DATABASE_FILE_PATH = get_path_from_root("/IMM_database/test.db")

_Base = declarative_base()

class _NoneFormatter(Formatter):
    """Custom Formatter class that handles formatting of None values."""
    
    def __init__(self, namespace={}):
        """Constructor, very similar to base constructor."""
        super().__init__()
        self.namespace = namespace

    def format_field(self, value, format_spec):
        """Format a value according to format_spec.

        If the value is None, it is formatted as "NULL", regardless of
        the format specifier. All other values are deferred to the
        base Formatter format_field method.

        value -- The value to format.
        format_spec -- A format specifier for value.
        """
        if value == None:
            return "NULL"
        else:
            return super().format_field(value, format_spec)


class Coordinate:
    """Column composite ORM class representing a coordinate.

    This class allows coordinates to be treated as a unit, despite them consisting
    of values stored in multiple columns. Coordinates are saved using latitude and
    longitude, each represented by degree as a float value.

    Inspired by this SQLAlchemy tutorial:
    https://docs.sqlalchemy.org/en/13/orm/composites.html
    """

    def __init__(self, lat, long):
        """Coordinate constructor.

        lat -- The latitute in degrees.
        long -- The longitude in degrees.
        """
        self.lat = lat
        self.long = long
    
    def __composite_values__(self):
        """Return a (lat, long) tuple."""
        return self.lat, self.long

    def __repr__(self):
        """Return a string describing the coordinate."""
        return _NoneFormatter().format("Coordinate(lat={}, long={})", self.lat, self.long)

    def __eq__(self, other):
        """Return True if self and other represent the same coordinate, else False."""
        return isinstance(other, Coordinate) and self.lat == other.lat and self.long == other.long

    def __ne__(self, other):
        """Return True if self and other represent different coordinates, else False."""
        return not self.__eq__(other)


class UserSession(_Base):
    """ORM class representing a situation where the IMM is used.

    UserSession is the central database class. All Images, Clients etc. are tied
    to one and only one UserSession object. The UserSession is used to determine
    which Images etc. a Client may access.

    UserSession has the following attributes:
    id              An integer that uniquely identifies the session. Used as the
                    primary database key. If unspecified, the database manager
                    automatically assigns a new id when the object is commited.
    clients         A list of Client objects associated with this UserSession.
    area_vertices   A list of AreaVertex objects associated with this UserSession.
    images          A list of Image objects associated with this UserSession.
    prio_images     A list of PrioImage objects associated with this USerSession.
    drones          A list of Drone objects associated with this UserSession.
    start_time      The time when the session started, given as a Unix timestamp.
                    Not nullable.
    end_time        The time when the session ended, given as a Unix timestamp.
                    Nullable.
    drone_mode      The current drone mode used in the session. Should be "AUTO"
                    for autonomous or "MAN" for manual mode.
    """

    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    start_time = Column(Integer, nullable=False)
    end_time = Column(Integer)
    drone_mode = Column(String, nullable=False)

    def __repr__(self):
        """Return a string representation of the UserSession."""
        return _NoneFormatter().format('<UserSession(id={:6d}, start_time={}, end_time={}, drone_mode={}', 
            self.id, self.start_time, self.end_time, self.drone_mode)


class Client(_Base):
    """ORM class representing a client interacting with a session.

    Clients are tied to a UserSession, and should only be allowed to access data
    ties to this UserSession. Clients have a view, describing the area the Client
    is currently viewing.

    Client has the following attributes:
    id              An integer that uniquely identifies the client. Used as the
                    primary database key. If unspecified, the database manager
                    automatically assigns a new id when the object is commited.
    session_id      The id of the UserSession associated with the Client. The
                    DBMS automatically synchronizes this with the session object.
                    Not nullable.
    session         The UserSession object associated with the Client. See
                    notes on session_id.
    up_left         A Coordinate describing the upper left corner of the
                    current view. Nullable.
    up_right        A Coordinate describing the upper right corner of the
                    current view. Nullable.
    down_right      A Coordinate describing the lower right corner of the
                    current view. Nullable.
    down_left       A Coordinate describing the lower left corner of the
                    current view. Nullable.
    center          A Coordinate describing the center point of the current
                    view. Nullable.
    """
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    __up_left_lat = Column(Float, nullable=True)
    __up_left_long = Column(Float, nullable=True)
    __up_right_lat = Column(Float, nullable=True)
    __up_right_long = Column(Float, nullable=True)
    __down_right_lat = Column(Float, nullable=True)
    __down_right_long = Column(Float, nullable=True)
    __down_left_lat = Column(Float, nullable=True)
    __down_left_long = Column(Float, nullable=True)
    __center_lat = Column(Float, nullable=True)
    __center_long = Column(Float, nullable=True)

    up_left = composite(Coordinate, __up_left_lat, __up_left_long)
    up_right = composite(Coordinate, __up_right_lat, __up_right_long)
    down_right = composite(Coordinate, __down_right_lat, __down_right_long)
    down_left = composite(Coordinate, __down_left_lat, __down_left_long)
    center = composite(Coordinate, __center_lat, __center_long)

    session = relationship("UserSession", back_populates="clients")

    def __repr__(self):
        """Return a string representation of the Client."""
        return _NoneFormatter().format('<Client(id={0:6d}, session_id={1:6d}, up_left={2}, up_right={3}, down_right={4}, down_left={5}',
            self.id, self.session_id, self.up_left, self.up_right, self.down_right, self.down_left)


UserSession.clients = relationship("Client", order_by=Client.id, back_populates="session")


class AreaVertex(_Base):
    """ORM class representing a vertex in the designated UserSession area.

    When starting a new session, an area is specified by the user. This area
    represents the safe area where drones are allowed to operate, as well as
    indicates the area of interest to the user. The area is represented by
    three or more AreaVertices uniquely determining a simple polygon.

    AreaVertex has the following attributes:
    session_id      The id of the UserSession associated with the AreaVertex.
                    The DBMS automatically synchronizes this with the session
                    object. Part of a composite primary key, together with
                    vertex_no.
    session         The UserSession object associated with the AreaVertex. See
                    notes on session_id.
    vertex_no       The position of the vertex when traversing the edge of the
                    area polygon. Note that different vertex orders result
                    in different polygons. Part of a composite primary key,
                    together with session_id.
    coordinate      A Coordinate describing the vertex position. Not nullable.
    """

    __tablename__ = 'areas'

    session_id = Column(Integer, ForeignKey('sessions.id'), primary_key=True)
    vertex_no = Column(Integer, primary_key=True, nullable=False)
    __coordinate_lat = Column(Float, nullable=False)
    __coordinate_long = Column(Float, nullable=False)
    
    coordinate = composite(Coordinate, __coordinate_lat, __coordinate_long)

    session = relationship("UserSession", back_populates="area_vertices")

    def __repr__(self):
        """Return a string representation of this AreaVertex."""
        return _NoneFormatter().format('<AreaVertex(session_id={0:6d}, vertex_no={1:6d}, coordinate={2}',
            self.session_id, self.vertex_no, self.coordinate.__repr__())


UserSession.area_vertices = relationship("AreaVertex", order_by=AreaVertex.vertex_no, back_populates="session")


class Image(_Base):
    """ORM class representing an Image received from RDS.

    When RDS published an image to the IMM backend, these are saved in
    a folder and tracked by the database. This class contains the necessary
    information about an image.

    Image has the following attributes:
    id          An integer that uniquely identifies the session. Used as the
                primary databsae key. If unspecified, the DBMS automatically
                assigns a new id when the object is commited.
    session_id  The id of the UserSession associated with the Image. The DBMS
                automatically synchronizes this with the session object. Not
                nullable.
    session     The UserSession object associated with the Image. See notes
                on session_id.
    prio_image  The PrioImage object representing the request made to take this
                image. If the image was not taken in respons to such a request,
                this attribute is None. Nullable.
    time_taken  The Unix timestamp when the image was taken. Not nullable.
    width       The image width in pixels. Not nullable.
    height      The image height in pixels. Not nullable.
    type        The image type, e.g. "IR" or "RGB". Not nullable.
    file_name   The name of the file where the image is stored. The image file
                is assumed to be located in the default image folder for the
                IMM.
    up_left     A Coordinate describing the location of the upper left corner
                of the image. Not nullable.
    up_right    A Coordinate describing the location of the upper right corner
                of the image. Not nullable.
    down_right  A Coordinate describing the location of the lower right corner
                of the image. Not nullable.
    down_left   A Coordinate describing the location of the lower right corner
                of the image. Not nullable.
    center      A Coordintae describing the location of the center point of the
                image. Not nullable.
    """
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
        """Return a string representation of the Image."""
        return _NoneFormatter().format('<Image(id={:6d}, session_id={:6d}, time_taken={}, width={:4d}px, height={:4d}px, type={}, up_left={}, up_right={}, down_right={}, down_left={}, file_path={}',
            self.id, self.session_id, self.time_taken, self.width, self.height, self.type, self.up_left.__repr__(), self.up_right.__repr__(), self.down_right.__repr__(), self.down_left.__repr__(), self.file_name)


UserSession.images = relationship("Image", order_by=Image.id, back_populates="session")


class PrioImage(_Base):
    """ORM class representing a prioritized image request.

    When using the system, the user may request that a prioritized image be
    taken showing a particular area. This class is used to track one such
    request.

    PrioImage has the following attributes:
    id              An integer that uniquely identifies the client. Used as the
                    primary database key. If unspecified, the DBMS automatically
                    assigns a new id when the object is commited.
    session_id      The id of the UserSession associated with the PrioImage. The
                    DBMS automatically synchronizes this with the session object.
                    Not nullable.
    session         The UserSession object associated with the PrioImage. See
                    notes on session_id.
    coordinate      The Coordinate where the image should be taken.
    time_requested  The Unix timestamp when the prioritized image was requested.
                    Not nullable.
    status          "PENDING" if the request is active and no image has yet been
                    received. "CANCELLED" if the request was cancelled by the user
                    or IMM system. "DELIVERED" if the image has been delivered
                    by RDS. Not nullable.
    image_id        The id if the image delivered by RDS as respons to this
                    requst. If no such image has been delivered, i.e. if status
                    is either "PENDING" or "CANCELLED", this attribute is set
                    to None. The DBMS automaticaly synchronizes this with the
                    image object. Not nullable.
    image           The image object delivered as a respons to this request. See
                    notes on image_id.
    eta             The estimated time when the image will be delivered, as a
                    Unix timestamp. If the ETA is not known, this attribute is
                    set to None. Nullable.
    """
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
        """Return a string representation of the object."""
        return _NoneFormatter().format('<PrioImage(id={0:6d}, session_id={1:6d}, time_requested={2}, coordinate={3}, status={4}, image_id={5:6d}, eta={6}',
            self.id, self.session_id, self.time_requested, self.coordinate.__repr__(), self.status, self.image_id, self.eta)


UserSession.prio_images = relationship("PrioImage", order_by=PrioImage.id, back_populates="session")
Image.prio_image = relationship("PrioImage", order_by=PrioImage.id, uselist=False, back_populates="image")


class Drone(_Base):
    """ORM class representing a drone active within a session.

    Each session has drones assigned to them. The drones themselves are managed
    by RDS, but it is possible to retrieve information about these drones. This
    information is regularly retrieved from RDS and stored to be immediately
    transmittable to a client on request.

    Drone has the following attributes:
    id              An integer that uniquely identifies the drone. Used as the
                    primary database key. If unspecified, the DBMS automatically
                    assigns a new id when the object is commited.
    session_id      The id of the UserSession associated with the Drone. The
                    DBMS automatically synchronizes this with the session object.
                    Not nullable.
    session         The UserSession object associated with the Droone. See notes
                    on session_id.
    last_updated    The Unix timestamp when the information was last updated.
                    Not nullable.
    eta             The Unix timestamp when the drone is estimated to reach its
                    current destination. Set to None if unknown. Nullable.
    """
    __tablename__ = 'drones'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    last_updated = Column(Integer, nullable=False)
    eta = Column(Integer, nullable=True)

    session = relationship("UserSession", back_populates="drones")

    def __repr__(self):
        """Return a string representation of the Drone."""
        return _NoneFormatter().format('<Drone(id={0:6d}, session_id={1:6d}, last_updated={2}, eta={3}',
            self.id, self.session_id, self.last_updated, self.eta)

UserSession.drones = relationship("Drone", order_by=Drone.id, back_populates="session")


@event.listens_for(Engine, "connect")
def __set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraint checks for a SQLite3 DBMS.

    Foreign key constraints are not enforced by default by SQLite3. A pragma
    command must be issued to the DBMS on connection to enable these checks.

    This function was provided by this blog post:
    https://www.scrygroup.com/tutorial/2018-05-07/SQLite-foreign-keys/
    """
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

class _Database:
    """A simple class used to manage thread-safe SQLAlchemy session objects."""

    def __init__(self, file_path, echo=False):
        """Database constructor.

        Sets up a new connection to a SQLite3 database file. Creates session
        factories used to create session objects.

        file_path   The absolute file path to the database file. If an in-memory
                    database is wanted, set this to ":memory:".
        echo        True if the engine should print SQL commands sent to the
                    DBMS, else False. (default False)
        """
        self.__engine = create_engine('sqlite:///' + file_path, echo=echo)
        _Base.metadata.create_all(bind=self.__engine)
        self.__session_maker = sessionmaker(bind=self.__engine)
        self.__Session = scoped_session(self.__session_maker)

        self.__session_cnt = 0
        self.__session_cnt_mutex = Lock()
        self.__session_active_sema = Semaphore()
        self.__session_active_sema.release() # Initialize to 1

    def get_session(self):
        """Return a new thread-safe session object."""
        self.__session_cnt_mutex.acquire()
        self.__session_cnt += 1
        if self.__session_cnt == 1:
            # Block disposing until session is released.
            self.__session_active_sema.acquire()
        self.__session_cnt_mutex.release()
        return self.__Session()

    def release_session(self):
        """Close and remove the session object used by the current thread."""
        self.__session_cnt_mutex.acquire()
        self.__session_cnt -= 1
        if self.__session_cnt == 0:
            # Allow disposing, since to sessions are active.
            self.__session_active_sema.release()
        self.__session_cnt_mutex.release()
        return self.__Session.remove()

    def dispose(self):
        # Don't procees if there are active sessions remaining.
        self.__session_active_sema.acquire()
        self.__engine.dispose()


__active_db = None
__change_active_db_mutex = Lock()

def use_production_db():
    """Sets the production database as the currently active database.

    Note that this setting affects all methods globally. Sessions retrieved
    using the session_scope context manager are connected to the production
    database if this setting is active. Any previously opened database is
    closed, though active connections to such database is kept alive until
    closed.
    """
    global __active_db
    __change_active_db_mutex.acquire()
    if __active_db:
        __active_db.dispose()
        __active_db = None
    __active_db = _Database(__PRODUCTION_DATABASE_FILE_PATH)
    __change_active_db_mutex.release()

def use_test_database(in_memory=True):
    """Sets a new test database as the currently active database.

    Note that this setting affects all methods globally. Sessions retrieved
    using the session_scope context manager are connected to the test
    database if this setting is active. Any previously opened database is
    closed, though active connections to such database is kept alive until
    closed.

    in_memory   If True, the test database is created as an in-memory database.
                This setting should be set to False if the test involves multiple
                threads accessing the database, as in-memory database access from
                multiple threads is not supported by SQLite3.
    """
    global __active_db
    __change_active_db_mutex.acquire()
    if __active_db:
        __active_db.dispose()
        __active_db = None
    if in_memory:
        __active_db = _Database(":memory:")
    else:
        if os.path.exists(__TEST_DATABASE_FILE_PATH):
            os.remove(__TEST_DATABASE_FILE_PATH)
        __active_db = _Database(__TEST_DATABASE_FILE_PATH)
    __change_active_db_mutex.release()

@contextmanager
def session_scope():
    """Context manager for database sessions.

    Sample usage:
    with session_scope() as session:
        session.DATABASE_QUERY

    Abstracts the handling of the session object. A new thread-safe session
    is created automatically, connected to the currently active database. When
    reaching the end of the with block, the session automatically tries to
    commit all uncommited changes. If the commit fails, or an exception is
    raised while processing the queries, a rollback of all changes is
    automatically performed and the exception is escalated. Regardless of
    the success or failure to commit, the session is automatically closed and
    released to the database at the end of the with block.

    Note that ORM objects retrieved using a session are no longer usable after
    the session has been closed. All changes must thus be performed within a
    single with block, or the objects has to be queried again from the new
    session object.

    This context manager is inspired by the SQLAlchemy session tutorial:
    https://docs.sqlalchemy.org/en/13/orm/session_basics.html
    """
    # Don't proceed if the current database is in the process of being closed.
    __change_active_db_mutex.acquire()
    session = __active_db.get_session()
    __change_active_db_mutex.release()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
        __active_db.release_session()

if __name__ == '__main__':
    with session_scope() as session:
        # The session only exists withing this with statement. Commit, rollback
        # and release are performed automatically by the context manager when
        # appropriate.
        for user_session in session.query(UserSession).all():
            print(user_session)