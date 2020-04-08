import unittest

from random import randint, uniform, seed
from time import sleep
from threading import Thread

from IMM_database.database import Coordinate
from IMM_database.database import UserSession, Client, AreaVertex, Image, PrioImage, Drone
from IMM_database.database import get_test_database

from sqlalchemy.exc import IntegrityError

class CoordinateTester(unittest.TestCase):
    def test_equality(self):
        self.assertEqual(Coordinate(1, 1), Coordinate(1, 1))
        self.assertEqual(Coordinate(-1, -1), Coordinate(-1, -1))
        self.assertNotEqual(Coordinate(1, 1), Coordinate(-1, -1))
        self.assertNotEqual(Coordinate(1, -1), Coordinate(-1, 1))
        self.assertNotEqual(Coordinate(1, 1), None)
        self.assertNotEqual(Coordinate(1, 1), self)

    def test_composite_values(self):
        self.assertEqual(Coordinate(1, 5).__composite_values__(), (1, 5))

    def test_eq(self):
        coord = Coordinate(1, 5)
        self.assertTrue(coord.__eq__(coord))
        self.assertTrue(coord.__eq__(Coordinate(1, 5)))
        self.assertFalse(coord.__eq__(Coordinate(10, -2)))
        self.assertFalse(coord.__eq__(Coordinate(1, -2)))
        self.assertFalse(coord.__eq__(Coordinate(2, 5)))
        self.assertFalse(coord.__eq__(None))
        self.assertFalse(coord.__eq__("test"))
        self.assertTrue(coord.__eq__(Coordinate(1, 5.0)))

    def test_ne(self):
        coord = Coordinate(1, 5)
        self.assertFalse(coord.__ne__(coord))
        self.assertFalse(coord.__ne__(Coordinate(1, 5)))
        self.assertTrue(coord.__ne__(Coordinate(10, -2)))
        self.assertTrue(coord.__ne__(Coordinate(1, -2)))
        self.assertTrue(coord.__ne__(Coordinate(2, 5)))
        self.assertTrue(coord.__ne__(None))
        self.assertTrue(coord.__ne__("test"))
        self.assertFalse(coord.__ne__(Coordinate(1, 5.0)))

    def test_repr(self):
        Coordinate(1, 1).__repr__()

class UserSessionTester(unittest.TestCase):
    
    def setUp(self):
        seed(123)   # Avoid flaky tests by using the same seed every time.
        self.db = get_test_database()
        self.session = self.db.get_session()

    def tearDown(self):
        self.db.release_session()

    def test_single_entry(self):
        self.session.add(UserSession(start_time=123, drone_mode="AUTO"))
        self.session.commit()

        self.assertEqual(len(self.session.query(UserSession).all()), 1,
            "Wrong number of entries.")
        self.assertEqual(self.session.query(UserSession).first().drone_mode, "AUTO",
            "Wrong drone mode retrieved.")
        self.assertEqual(self.session.query(UserSession.drone_mode).filter(UserSession.end_time == None).scalar(), "AUTO", 
            "Wrong drone mode retrieved when filtering.")
        self.assertEqual(len(self.session.query(UserSession).filter(UserSession.end_time == 123).all()), 0,
            "Failed to filter by nonexistant property.")

    def test_multiple_unique_entries(self):
        n_sessions = 500

        start_times = [randint(100000, 200000) for i in range(n_sessions)]
        drone_modes = ["AUTO" if randint(0, 1) == 0 else "MAN" for i in range(n_sessions)]
        user_sessions = [UserSession(start_time=start_times[i], drone_mode = drone_modes[i]) for i in range(n_sessions)]
        for session in user_sessions:
            self.session.add(session)
        self.session.commit()

        sessions_in_database = self.session.query(UserSession).\
            order_by(UserSession.id).all()
        self.assertEqual(len(sessions_in_database), n_sessions,
            "Incorrect number of entries saved in IMM_database.")
        for i in range(n_sessions):
            with self.subTest(i=i):
                self.assertTrue(user_sessions[i] is sessions_in_database[i],
                    "Retrieved session is not the same object as created session.")
                self.assertEqual(start_times[i], sessions_in_database[i].start_time,
                    "Retrieved session has incorrect start time.")
                self.assertEqual(drone_modes[i], sessions_in_database[i].drone_mode,
                    "Retrieved session has incorrect done mode.")
                self.assertIsNone(sessions_in_database[i].end_time)
        self.assertEqual(len(self.session.query(UserSession).\
            filter(UserSession.end_time != None).all()), 0,
            "Found nonexistant session.")
    
    def test_repr(self):
        UserSession(start_time=123, drone_mode="MAN").__repr__()

    def test_not_nullable(self):
        def check_invalid(session):
            self.session.add(session)
            with self.assertRaises(IntegrityError, msg="Nullable constraint not met."):
                self.session.commit()
            self.session.rollback()

        check_invalid(UserSession(start_time=123))
        check_invalid(UserSession(drone_mode="MAN"))

class ClientTester(unittest.TestCase):
    
    def setUp(self):
        self.SESSIONS = 5

        seed(123)   # Avoid flaky tests by using the same seed every time.
        self.db = get_test_database()
        self.session = self.db.get_session()
        for _i in range(self.SESSIONS):
            self.session.add(UserSession(start_time=randint(100000, 200000),
                                         end_time=randint(200000, 300000),
                                         drone_mode="AUTO"))
        self.session.commit()

    def tearDown(self):
        self.db.release_session()

    def test_single_entry(self):
        client = Client(session_id=self.SESSIONS // 2)
        client.up_left = Coordinate(1, 5)
        client.up_right = Coordinate(5, 5)
        client.down_right = Coordinate(5, 1)
        client.down_left = Coordinate(1, 1)
        self.session.add(client)
        self.session.commit()
        
        self.assertEqual(len(self.session.query(Client).all()), 1,
            "Wrong number of entries.")
        self.assertEqual(self.session.query(Client).first().up_left, Coordinate(1, 5),
            "Wrong view retrieved.")
        self.assertEqual(len(self.session.query(Client).filter(Client.up_left == Coordinate(3, 3)).all()), 0,
            "Failed to filter by nonexistant property.")

    def test_multiple_unique_entries(self):
        n_clients = 500

        up_left = [Coordinate(uniform(1, 5), uniform(5, 10)) for i in range(n_clients)]
        up_right = [Coordinate(uniform(5, 10), uniform(5, 10)) for i in range(n_clients)]
        down_right = [Coordinate(uniform(5, 10), uniform(1, 5)) for i in range(n_clients)]
        down_left = [Coordinate(uniform(1, 5), uniform(1, 5)) for i in range(n_clients)]
        sessions = [randint(1, self.SESSIONS) for i in range(n_clients)]
        clients = [Client(
            session_id=sessions[i],
            up_left=up_left[i], up_right=up_right[i],
            down_right=down_right[i], down_left=down_left[i]
            ) for i in range(n_clients)]
        for client in clients:
            self.session.add(client)
        self.session.commit()

        clients_in_database = self.session.query(Client).\
            order_by(Client.id).all()
        self.assertEqual(len(clients_in_database), n_clients,
            "Incorrect number of entries saved in IMM_database.")
        for i in range(n_clients):
            with self.subTest(i=i):
                self.assertTrue(clients[i] is clients_in_database[i],
                    "Retrieved session is not the same object as created session.")
        self.assertEqual(len(self.session.query(Client).\
            filter(Client.up_left == Coordinate(0, 0)).all()), 0,
            "Found nonexistant session.")

    def test_repr(self):
        Client(
            session_id=1,
            up_left=Coordinate(1, 5),
            up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1),
            down_left=Coordinate(1, 1)
        ).__repr__()

    def test_not_nullable(self):
        def check_invalid(client):
            self.session.add(client)
            with self.assertRaises(IntegrityError, msg="Nullable constraint not met."):
                self.session.commit()
            self.session.rollback()

        up_left = Coordinate(1, 5)
        up_right = Coordinate(5, 5)
        down_right = Coordinate(5, 1)
        down_left = Coordinate(1, 1)
        check_invalid(Client(up_left=up_left, up_right=up_right, down_right=down_right, down_left=down_left))
        check_invalid(Client(session_id=1, up_right=up_right, down_right=down_right, down_left=down_left))
        check_invalid(Client(session_id=1, up_left=up_left, down_right=down_right, down_left=down_left))
        check_invalid(Client(session_id=1, up_left=up_left, up_right=up_right, down_left=down_left))
        check_invalid(Client(session_id=1, up_left=up_left, up_right=up_right, down_right=down_right))

    def test_foreign_key(self):
        self.session.add(Client(
            session_id=self.SESSIONS + 1,
            up_left=Coordinate(1, 5),
            up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1),
            down_left=Coordinate(1, 1)
        ))
        with self.assertRaises(IntegrityError, msg="Foreign key contraint not met."):
            self.session.commit()


class AreaVertexTester(unittest.TestCase):
    
    def setUp(self):
        self.SESSIONS = 5

        seed(123)   # Avoid flaky tests by using the same seed every time.
        self.db = get_test_database()
        self.session = self.db.get_session()
        for _i in range(self.SESSIONS):
            self.session.add(UserSession(start_time=randint(100000, 200000),
                                         end_time=randint(200000, 300000),
                                         drone_mode="AUTO"))
        self.session.commit()

    def tearDown(self):
        self.db.release_session()

    def test_single_entry(self):
        vertex = AreaVertex(session_id=randint(1, self.SESSIONS),
            vertex_no=1, coordinate=Coordinate(lat=1.5, long=0.23))
        self.session.add(vertex)
        self.session.commit()
        
        self.assertEqual(self.session.query(AreaVertex).count(), 1,
            "Wrong number of entries.")
        self.assertEqual(self.session.query(AreaVertex).first().coordinate, Coordinate(1.5, 0.23),
            "Wrong vertex retrieved.")
        self.assertTrue(self.session.query(AreaVertex).filter(AreaVertex.coordinate == Coordinate(1.5, 0.23)).first() is vertex,
            "Failed to filter by coordinate.")
        self.assertEqual(self.session.query(AreaVertex).filter(AreaVertex.coordinate == Coordinate(1.5, 1.5)).count(), 0,
            "Failed to filter by nonexistant property.")

    def test_multiple_unique_entries(self):
        n_max_vertices = 100
        n_vertices_for_session = [randint(1, n_max_vertices) for i in range(self.SESSIONS)]
        coordinates = [[Coordinate(uniform(1, 100), uniform(1, 100)) for i in range(j)] for j in n_vertices_for_session]
        vertices = [[AreaVertex(session_id=i+1, vertex_no=j, coordinate=coordinates[i][j]) for j in range(n_vertices_for_session[i])] for i in range(self.SESSIONS)]
        for session_vertices in vertices:
            for vertex in session_vertices:
                self.session.add(vertex)
        self.session.commit()

        n_vertices_in_database = self.session.query(AreaVertex).\
            order_by(AreaVertex.session_id, AreaVertex.vertex_no).count()
        self.assertEqual(n_vertices_in_database, sum(n_vertices_for_session),
            "Incorrect number of entries saved in database.")
        for session_id in range(self.SESSIONS):
            with self.subTest(i=session_id):
                session_vertices = self.session.query(AreaVertex).filter(AreaVertex.session_id == session_id+1).all()
                self.assertEqual(len(session_vertices), n_vertices_for_session[session_id],
                    "Incorrect number of vertices retrieved for session.")
                for i in range(n_vertices_for_session[session_id]):
                    with self.subTest(i=i):
                        self.assertTrue(vertices[session_id][i] is session_vertices[i],
                            "Retrieved vertex is not the same object as created vertex.")
        self.assertEqual(self.session.query(AreaVertex).\
            filter(AreaVertex.coordinate == Coordinate(-1, -1)).count(), 0,
            "Found nonexistant vertex.")
    
    def test_repr(self):
        AreaVertex(session_id=1, vertex_no=1, coordinate=Coordinate(1, 1)).__repr__()

    def test_not_nullable(self):
        def check_invalid(vertex):
            self.session.add(vertex)
            with self.assertRaises(IntegrityError, msg="Nullable constraint not met."):
                self.session.commit()
            self.session.rollback()

        coordinate = Coordinate(13.2, 175.4)
        check_invalid(AreaVertex(vertex_no=1, coordinate=coordinate))
        check_invalid(AreaVertex(session_id=1, coordinate=coordinate))
        check_invalid(AreaVertex(session_id=1, vertex_no=1))

    def test_foreign_key(self):
        self.session.add(AreaVertex(
            session_id=self.SESSIONS + 1,
            vertex_no=1,
            coordinate=Coordinate(5, 5)
        ))
        with self.assertRaises(IntegrityError, msg="Foreign key contraint not met."):
            self.session.commit()

class ImageTester(unittest.TestCase):
    
    def setUp(self):
        self.SESSIONS = 5

        seed(123)   # Avoid flaky tests by using the same seed every time.
        self.db = get_test_database()
        self.session = self.db.get_session()
        for _i in range(self.SESSIONS):
            self.session.add(UserSession(
                start_time=randint(100000, 200000),
                end_time=randint(200000, 300000),
                drone_mode="AUTO"
            ))
        self.session.commit()

    def tearDown(self):
        self.db.release_session()

    def test_single_entry(self):
        image = Image(
            session_id=randint(1, self.SESSIONS),
            time_taken=randint(100000, 200000), 
            width=480, height=360, type="IR",
            up_left=Coordinate(1, 5),
            up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1),
            down_left=Coordinate(1, 1),
            center=Coordinate(3, 3),
            file_name="images/1.jpg"
        )
        self.session.add(image)
        self.session.commit()
        
        self.assertEqual(self.session.query(Image).count(), 1,
            "Wrong number of entries.")
        self.assertEqual(self.session.query(Image.width).first()[0], 480,
            "Wrong width retrieved.")
        self.assertTrue(self.session.query(Image).filter(Image.height == 360).first() is image,
            "Failed to filter by coordinate.")
        self.assertEqual(self.session.query(Image).filter(Image.type == "LASERBEAM").count(), 0,
            "Failed to filter by nonexistant property.")

    def test_multiple_unique_entries(self):
        n_images = 500
        session = [randint(1, self.SESSIONS) for i in range(n_images)]
        time_taken = [randint(100000, 200000) for i in range(n_images)]
        width = [randint(100, 1000) for i in range(n_images)]
        height = [randint(100, 1000) for i in range(n_images)]
        type = ["IR" for i in range(n_images)]
        up_left = [Coordinate(uniform(1, 100), uniform(100, 200)) for i in range(n_images)]
        up_right = [Coordinate(uniform(100, 200), uniform(100, 200)) for i in range(n_images)]
        down_right = [Coordinate(uniform(100, 200), uniform(1, 100)) for i in range(n_images)]
        down_left = [Coordinate(uniform(1, 100), uniform(1, 100)) for i in range(n_images)]
        center = [Coordinate(100, 100) for i in range(n_images)]
        file_name = ["{}.jpg".format(i) for i in range(n_images)]

        images = [Image(
            session_id=session[i],
            time_taken=time_taken[i],
            width=width[i],
            height=height[i],
            type=type[i],
            up_left=up_left[i],
            up_right=up_right[i],
            down_right=down_right[i],
            down_left=down_left[i],
            center=center[i],
            file_name=file_name[i]
        ) for i in range(n_images)]
        for image in images:
            self.session.add(image)
        self.session.commit()

        self.assertEqual(self.session.query(Image).count(), n_images,
            "Incorrect number of entries saved in database.")
        for session_id in range(self.SESSIONS):
            with self.subTest(i=session_id):
                n_session_images = self.session.query(Image).filter(Image.session_id == session_id).count()
                self.assertEqual(n_session_images, session.count(session_id),
                    "Incorrect number of images retrieved for session.")
        images_in_database = self.session.query(Image).order_by(Image.id).all()
        for i in range(n_images):
            with self.subTest(i=i):
                self.assertTrue(images_in_database[i] is images[i],
                    "Retrieved Image is not the same object as inserted Image.")
        self.assertEqual(self.session.query(Image).\
            filter(Image.width == 0).count(), 0,
            "Found nonexistant vertex.")

    def test_repr(self):
        Image(
            session_id=1,
            time_taken=123,
            width=100,
            height=200,
            type="IR",
            up_left=Coordinate(1, 5),
            up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1),
            down_left=Coordinate(1, 1),
            center=Coordinate(3, 3),
            file_name="1.jpg"
        ).__repr__()

    def test_not_nullable(self):
        def check_invalid(image):
            self.session.add(image)
            with self.assertRaises(IntegrityError, msg="Nullable constraint not met."):
                self.session.commit()
            self.session.rollback()

        check_invalid(Image(
            time_taken=100000,
            width=240, height=360, type="IR",
            up_left=Coordinate(1, 5), up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1), down_left=Coordinate(1, 1),
            file_name="1.jpg"
        ))
        check_invalid(Image(
            session_id=1,
            width=240, height=360, type="IR",
            up_left=Coordinate(1, 5), up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1), down_left=Coordinate(1, 1),
            file_name="1.jpg"
        ))
        check_invalid(Image(
            session_id=1, time_taken=100000,
            height=360, type="IR",
            up_left=Coordinate(1, 5), up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1), down_left=Coordinate(1, 1),
            file_name="1.jpg"
        ))
        check_invalid(Image(
            session_id=1, time_taken=100000,
            width=240, type="IR",
            up_left=Coordinate(1, 5), up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1), down_left=Coordinate(1, 1),
            file_name="1.jpg"
        ))
        check_invalid(Image(
            session_id=1, time_taken=100000,
            width=240, height=360,
            up_left=Coordinate(1, 5), up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1), down_left=Coordinate(1, 1),
            file_name="1.jpg"
        ))
        check_invalid(Image(
            session_id=1, time_taken=100000,
            width=240, height=360, type="IR",
            up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1), down_left=Coordinate(1, 1),
            file_name="1.jpg"
        ))
        check_invalid(Image(
            session_id=1, time_taken=100000,
            width=240, height=360, type="IR",
            up_left=Coordinate(1, 5),
            down_right=Coordinate(5, 1), down_left=Coordinate(1, 1),
            file_name="1.jpg"
        ))
        check_invalid(Image(
            session_id=1, time_taken=100000,
            width=240, height=360, type="IR",
            up_left=Coordinate(1, 5), up_right=Coordinate(5, 5),
            down_left=Coordinate(1, 1),
            file_name="1.jpg"
        ))
        check_invalid(Image(
            session_id=1, time_taken=100000,
            width=240, height=360, type="IR",
            up_left=Coordinate(1, 5), up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1),
            file_name="1.jpg"
        ))
        check_invalid(Image(
            session_id=1, time_taken=100000,
            width=240, height=360, type="IR",
            up_left=Coordinate(1, 5), up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1), down_left=Coordinate(1, 1),
        ))

    def test_foreign_key(self):
        self.session.add(Image(
            session_id=self.SESSIONS+1,
            time_taken=123,
            width=100,
            height=200,
            type="IR",
            up_left=Coordinate(1, 5),
            up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1),
            down_left=Coordinate(1, 1),
            center=Coordinate(3, 3),
            file_name="1.jpg"
        ))
        with self.assertRaises(IntegrityError, msg="Foreign key contraint not met."):
            self.session.commit()

class PrioImageTester(unittest.TestCase):
    
    def setUp(self):
        self.SESSIONS = 5

        seed(123)   # Avoid flaky tests by using the same seed every time.
        self.db = get_test_database()
        self.session = self.db.get_session()
        for _i in range(self.SESSIONS):
            self.session.add(UserSession(
                start_time=randint(100000, 200000),
                end_time=randint(200000, 300000),
                drone_mode="AUTO"
            ))
        self.session.commit()

    def tearDown(self):
        self.db.release_session()

    def test_single_entry(self):
        image = PrioImage(
            session_id=randint(1, self.SESSIONS),
            time_requested=randint(100000, 200000),
            status="PENDING", eta=randint(100, 1000),
            coordinate=Coordinate(uniform(1, 5), uniform(1, 5))
        )
        self.session.add(image)
        self.session.commit()
        
        self.assertEqual(self.session.query(PrioImage).count(), 1,
            "Wrong number of entries.")
        self.assertEqual(self.session.query(PrioImage.status).first()[0],
            "PENDING", "Wrong vertex retrieved.")
        self.assertTrue(self.session.query(PrioImage).\
            filter(PrioImage.status == "PENDING").first() is image,
            "Failed to filter by status.")
        self.assertEqual(self.session.query(PrioImage).\
            filter(PrioImage.time_requested == 0).count(), 0,
            "Failed to filter by nonexistant property.")

    def test_multiple_unique_entries(self):
        n_images = 100
        session_ids = [randint(1, self.SESSIONS) for i in range(n_images)]
        time_requested = [randint(100000, 200000) for i in range(n_images)]
        status = ["CANCELLED" for i in range(n_images)]
        coordinates = [Coordinate(uniform(10, 20), uniform(10, 20)) for i in range(n_images)]
        images = [PrioImage(
            session_id=session_ids[i], time_requested=time_requested[i],
            status=status[i], coordinate=coordinates[i]
        ) for i in range(n_images)]
        for image in images:
            self.session.add(image)
        self.session.commit()

        n_images_in_database = self.session.query(PrioImage).order_by(PrioImage.id).count()
        self.assertEqual(n_images_in_database, n_images,
            "Incorrect number of entries saved in database.")
        for session_id in range(self.SESSIONS):
            with self.subTest(i=session_id):
                n_session_images = self.session.query(PrioImage).\
                    filter(PrioImage.session_id == session_id).count()
                self.assertEqual(n_session_images,
                    session_ids.count(session_id),
                    "Incorrect number of images retrieved for session.")
        for i in range(n_images):
            with self.subTest(i=i):
                self.assertTrue(self.session.query(PrioImage).\
                    filter(PrioImage.id == i + 1).first() is images[i],
                    "Retrieved image is not the same object as created image.")
        self.assertEqual(self.session.query(PrioImage).\
            filter(PrioImage.session_id == self.SESSIONS + 1).count(), 0,
            "Found nonexistant image.")

    def test_repr(self):
        PrioImage(
            session_id=1,
            time_requested=123,
            status="PENDING",
        ).__repr__()

    def test_not_nullable(self):
        def check_invalid(image):
            self.session.add(image)
            with self.assertRaises(IntegrityError, msg="Nullable constraint not met."):
                self.session.commit()
            self.session.rollback()

        check_invalid(PrioImage(time_requested=150000, status="COMPLETE"))
        check_invalid(PrioImage(session_id=1, status="COMPLETE"))
        check_invalid(PrioImage(session_id=1, time_requested=150000))

    def test_foreign_key(self):
        self.session.add(Image(
            session_id=1,
            time_taken=123,
            width=100,
            height=200,
            type="IR",
            up_left=Coordinate(1, 5),
            up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1),
            down_left=Coordinate(1, 1),
            center=Coordinate(3, 3),
            file_name="1.jpg"
        ))
        self.session.commit()

        self.session.add(PrioImage(
            session_id=self.SESSIONS+1,
            time_requested=123,
            status="PENDING",
            eta=123,
            coordinate=Coordinate(5, 4)
        ))
        with self.assertRaises(IntegrityError, msg="Foreign key contraint not met."):
            self.session.commit()
        self.session.rollback()

        self.session.add(PrioImage(
            session_id=1,
            image_id=2,
            time_requested=123,
            status="PENDING",
            eta=123,
            coordinate=Coordinate(5, 4)
        ))
        with self.assertRaises(IntegrityError, msg="Foreign key contraint not met."):
            self.session.commit()

class DroneTester(unittest.TestCase):
    
    def setUp(self):
        self.SESSIONS = 5

        seed(123)   # Avoid flaky tests by using the same seed every time.
        self.db = get_test_database()
        self.session = self.db.get_session()
        for _i in range(self.SESSIONS):
            self.session.add(UserSession(
                start_time=randint(100000, 200000),
                end_time=randint(200000, 300000),
                drone_mode="AUTO"
            ))
        self.session.commit()

    def tearDown(self):
        self.db.release_session()

    def test_single_entry(self):
        drone = Drone(
            session_id=1,
            last_updated=randint(100000, 200000),
            eta=randint(100, 1000)
        )
        self.session.add(drone)
        self.session.commit()
        
        self.assertEqual(self.session.query(Drone).count(), 1,
            "Wrong number of entries.")
        self.assertTrue(self.session.query(Drone).first() is drone,
            "Wrong drone retrieved.")
        self.assertTrue(self.session.query(Drone).\
            filter(Drone.session_id == 1).first() is drone,
            "Failed to filter by status.")
        self.assertEqual(self.session.query(Drone).\
            filter(Drone.eta == 2000).count(), 0,
            "Failed to filter by nonexistant property.")

    def test_multiple_unique_entries(self):
        n_drones = 100
        session_ids = [randint(1, self.SESSIONS) for i in range(n_drones)]
        last_updated = [randint(100000, 200000) for i in range(n_drones)]
        eta = [randint(100, 1000) for i in range(n_drones)]
        drones = [Drone(
            session_id=session_ids[i], last_updated=last_updated[i], eta=eta[i]
        ) for i in range(n_drones)]
        for drone in drones:
            self.session.add(drone)
        self.session.commit()

        n_drones_in_database = self.session.query(Drone).count()
        self.assertEqual(n_drones_in_database, n_drones,
            "Incorrect number of entries saved in database.")
        for session_id in range(self.SESSIONS):
            with self.subTest(i=session_id):
                n_session_drones = self.session.query(Drone).\
                    filter(Drone.session_id == session_id).count()
                self.assertEqual(n_session_drones,
                    session_ids.count(session_id),
                    "Incorrect number of drones retrieved for session.")
        for i in range(n_drones):
            with self.subTest(i=i):
                self.assertTrue(self.session.query(Drone).\
                    filter(Drone.id == i + 1).first() is drones[i],
                    "Retrieved drone is not the same object as created drone.")
        self.assertEqual(self.session.query(Drone).\
            filter(Drone.session_id == self.SESSIONS + 1).count(), 0,
            "Found nonexistant drone.")

    def test_repr(self):
        Drone(session_id=1).__repr__()

    def test_not_nullable(self):
        def check_invalid(image):
            self.session.add(image)
            with self.assertRaises(IntegrityError, msg="Nullable constraint not met."):
                self.session.commit()
            self.session.rollback()

        check_invalid(Drone())

    def test_foreign_key(self):
        self.session.add(Drone(session_id=self.SESSIONS + 1))
        with self.assertRaises(IntegrityError, msg="Foreign key contraint not met."):
            self.session.commit()

class RelationTester(unittest.TestCase):
    def setUp(self):
        seed(123)   # Avoid flaky tests by using the same seed every time.
        self.db = get_test_database()
        self.session = self.db.get_session()

    def tearDown(self):
        self.db.release_session()

    def testSessionClientRelation(self):
        session = UserSession(id=1, start_time=100, end_time=200, drone_mode="AUTO")
        client = Client(
            session_id=session.id,
            up_left=Coordinate(1, 5), up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1), down_left=Coordinate(1, 1)
        )
        self.session.add(session)
        self.session.add(client)
        self.session.commit()

        self.assertTrue(self.session.query(Client).first().session is session,
            "Wrong session retrieved from client.")
        self.assertTrue(self.session.query(UserSession).first().clients[0] is client,
            "Wrong client retrieved from session.")
        
        session.clients.append(Client(session_id=session.id,
            up_left=Coordinate(1, 5), up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1), down_left=Coordinate(1, 1)))
        self.session.commit()

        self.assertEqual(self.session.query(Client).count(), 2,
            "Failed to add Client via UserSession.clients.")
        self.assertEqual(len(self.session.query(UserSession).first().clients), 2,
            "Failed to retrieve all clients from UserSession.clients.")
        retrieved_clients = self.session.query(Client).order_by(Client.id).all()
        self.assertTrue(retrieved_clients[0] is client)
        self.assertTrue(retrieved_clients[0].session is session)
        self.assertFalse(retrieved_clients[1] is client)
        self.assertTrue(retrieved_clients[1].session is session)

    def testSessionAreaVertexRelation(self):
        session = UserSession(id=1, start_time=100, end_time=200, drone_mode="AUTO")
        vertex = AreaVertex(session_id=1, vertex_no=1, coordinate=Coordinate(1, 5))
        self.session.add(session)
        self.session.add(vertex)
        self.session.commit()

        self.assertTrue(self.session.query(AreaVertex).first().session is session,
            "Wrong session retrieved from vertex.")
        self.assertTrue(self.session.query(UserSession).first().area_vertices[0] is vertex,
            "Wrong vertex retrieved from session.")
        
        session.area_vertices.append(AreaVertex(
            session_id=1, vertex_no=2, coordinate=Coordinate(5, 1)
        ))
        self.session.commit()

        self.assertEqual(self.session.query(AreaVertex).count(), 2,
            "Failed to add AreaVertex via UserSession.area_vertices.")
        self.assertEqual(len(self.session.query(UserSession).first().area_vertices), 2,
            "Failed to retrieve all vertices from UserSession.area_verices.")
        retrieved_vertices = self.session.query(AreaVertex).order_by(AreaVertex.vertex_no).all()
        self.assertTrue(retrieved_vertices[0] is vertex)
        self.assertTrue(retrieved_vertices[0].session is session)
        self.assertFalse(retrieved_vertices[1] is vertex)
        self.assertTrue(retrieved_vertices[1].session is session)

    def testSessionImageRelation(self):
        session = UserSession(id=1, start_time=100, end_time=200, drone_mode="AUTO")
        image = Image(
            session_id=1,
            time_taken=123,
            width=100,
            height=200,
            type="IR",
            up_left=Coordinate(1, 5),
            up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1),
            down_left=Coordinate(1, 1),
            center=Coordinate(3, 3),
            file_name="1.jpg"
        )
        self.session.add(session)
        self.session.add(image)
        self.session.commit()

        self.assertTrue(self.session.query(Image).first().session is session,
            "Wrong session retrieved from image.")
        self.assertTrue(self.session.query(UserSession).first().images[0] is image,
            "Wrong image retrieved from session.")
        
        session.images.append(Image(
            time_taken=234,
            width=100,
            height=200,
            type="IR",
            up_left=Coordinate(1, 5),
            up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1),
            down_left=Coordinate(1, 1),
            center=Coordinate(3, 3),
            file_name="1.jpg"            
        ))
        self.session.commit()

        self.assertEqual(self.session.query(Image).count(), 2,
            "Failed to add Image via UserSession.images.")
        self.assertEqual(len(self.session.query(UserSession).first().images), 2,
            "Failed to retrieve all images from UserSession.images.")
        retrieved_images = self.session.query(Image).order_by(Image.id).all()
        self.assertTrue(retrieved_images[0] is image)
        self.assertTrue(retrieved_images[0].session is session)
        self.assertFalse(retrieved_images[1] is image)
        self.assertTrue(retrieved_images[1].session is session)

    def testSessionPrioImageRelation(self):
        session = UserSession(id=1, start_time=100, end_time=200, drone_mode="AUTO")
        prio_image = PrioImage(
            session_id=1,
            time_requested=123,
            status="PENDING",
            coordinate=Coordinate(lat=3, long=3)
        )
        self.session.add(session)
        self.session.add(prio_image)
        self.session.commit()

        self.assertTrue(self.session.query(PrioImage).first().session is session,
            "Wrong session retrieved from image.")
        self.assertTrue(self.session.query(UserSession).first().prio_images[0] is prio_image,
            "Wrong image retrieved from session.")
        
        session.prio_images.append(PrioImage(
            time_requested=234,
            status="CANCELLED",
            coordinate=Coordinate(lat=1, long=1)     
        ))
        self.session.commit()

        self.assertEqual(self.session.query(PrioImage).count(), 2,
            "Failed to add PrioImage via UserSession.prio_images.")
        self.assertEqual(len(self.session.query(UserSession).first().prio_images), 2,
            "Failed to retrieve all images from UserSession.prio_images.")
        retrieved_images = self.session.query(PrioImage).order_by(PrioImage.id).all()
        self.assertTrue(retrieved_images[0] is prio_image)
        self.assertTrue(retrieved_images[0].session is session)
        self.assertFalse(retrieved_images[1] is prio_image)
        self.assertTrue(retrieved_images[1].session is session)

    def testSessionDroneRelation(self):
        session = UserSession(id=1, start_time=100, end_time=200, drone_mode="AUTO")
        drone = Drone(session_id=1)
        self.session.add(session)
        self.session.add(drone)
        self.session.commit()

        self.assertTrue(self.session.query(Drone).first().session is session,
            "Wrong session retrieved from drone.")
        self.assertTrue(self.session.query(UserSession).first().drones[0] is drone,
            "Wrong drone retrieved from session.")
        
        session.drones.append(Drone(session_id=1, last_updated=123))
        self.session.commit()

        self.assertEqual(self.session.query(Drone).count(), 2,
            "Failed to add Drone via UserSession.drones.")
        self.assertEqual(len(self.session.query(UserSession).first().drones), 2,
            "Failed to retrieve all drones from UserSession.drones.")
        retrieved_drones = self.session.query(Drone).order_by(Drone.id).all()
        self.assertTrue(retrieved_drones[0] is drone)
        self.assertTrue(retrieved_drones[0].session is session)
        self.assertFalse(retrieved_drones[1] is drone)
        self.assertTrue(retrieved_drones[1].session is session)

    def testImagePrioImageRelation(self):
        session = UserSession(id=1, start_time=100, end_time=200, drone_mode="AUTO")
        image = Image(
            session_id=1,
            time_taken=234,
            width=100,
            height=200,
            type="IR",
            up_left=Coordinate(1, 5),
            up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1),
            down_left=Coordinate(1, 1),
            center=Coordinate(3, 3),
            file_name="1.jpg"               
        )
        prio_image = PrioImage(
            session_id=1,
            image_id=1,
            time_requested=123,
            status="PENDING",
            coordinate=Coordinate(lat=3, long=3)
        )
        self.session.add(session)
        self.session.add(image)
        self.session.add(prio_image)
        self.session.commit()

        self.assertTrue(self.session.query(PrioImage).first().image is image,
            "Wrong image retrieved from prioimage.")
        self.assertTrue(self.session.query(Image).first().prio_image is prio_image,
            "Wrong prioimage retrieved from image.")
        
        self.session.add(Image(
            session_id=1,
            time_taken=345,
            width=100,
            height=200,
            type="IR",
            up_left=Coordinate(1, 5),
            up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1),
            down_left=Coordinate(1, 1),
            center=Coordinate(3, 3),
            file_name="1.jpg",
            prio_image=prio_image
        ))
        self.session.commit()

        self.assertEqual(self.session.query(PrioImage).count(), 1,
            "Failed to move PrioImage relation via Image.prio_image.")
        self.assertFalse(prio_image.image is image,
            "Failed to move PrioImage relation via Image.prio_image.")
        self.assertIsNone(image.prio_image,
            "Failed to move PrioImage relation via Image.prio_image.")
        self.assertTrue(self.session.query(Image).filter(Image.id==2).first().prio_image is prio_image,
            "Failed to move PrioImage relation via Image.prio_image.")

class DatabaseConcurrencyTester(unittest.TestCase):

    def insert_sessions(self, n_sessions):
        session = self.db.get_session()
        for i in range(n_sessions):
            session.add(UserSession(start_time=i, end_time=i, drone_mode="AUTO"))
            sleep(0.01)
        self.assertEqual(len(session.new), n_sessions,
            "Wrong number of UserSessions added to session.")
        session.commit()
        self.assertEqual(len(session.new), 0,
            "New UserSessions present after commit")
        self.db.release_session()

    def setUp(self):
        self.db = get_test_database(in_memory=False)

    def tearDown(self):
        pass

    def run_threads(self, func, n_threads):
        results = [None for i in range(n_threads)]

        def wrapper(i):
            nonlocal results
            try:
                func()
            except Exception as e:
                results[i] = e
        
        threads = [Thread(target=lambda: wrapper(i)) for i in range(n_threads)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        return results

    def test_concurrency(self):
        n_threads = 10
        n_sessions_per_thread = 10
        results = self.run_threads(lambda: self.insert_sessions(n_sessions_per_thread), n_threads)
        for res in results:
            self.assertIsNone(res)
        session = self.db.get_session()
        self.assertEqual(session.query(UserSession).count(), n_threads * n_sessions_per_thread,
            "Incorrect number of sessions commited to database")

if __name__ == "__main__":
    unittest.main()