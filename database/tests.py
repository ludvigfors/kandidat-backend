import unittest
from random import randint, uniform, seed

from database import Coordinate
from database import UserSession, Client, AreaVertex, Coordinate, Image
from database import get_test_database

from sqlalchemy.exc import IntegrityError

class CoordinateTester(unittest.TestCase):
    def test_equality(self):
        self.assertEqual(Coordinate(1, 1), Coordinate(1, 1))
        self.assertEqual(Coordinate(-1, -1), Coordinate(-1, -1))
        self.assertNotEqual(Coordinate(1, 1), Coordinate(-1, -1))
        self.assertNotEqual(Coordinate(1, -1), Coordinate(-1, 1))
        self.assertNotEqual(Coordinate(1, 1), None)
        self.assertNotEqual(Coordinate(1, 1), self)

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
            "Incorrect number of entries saved in database.")
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
            "Incorrect number of entries saved in database.")
        for i in range(n_clients):
            with self.subTest(i=i):
                self.assertTrue(clients[i] is clients_in_database[i],
                    "Retrieved session is not the same object as created session.")
        self.assertEqual(len(self.session.query(Client).\
            filter(Client.up_left == Coordinate(0, 0)).all()), 0,
            "Found nonexistant session.")

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
            vertex_no=1, coordinate=Coordinate(x=1.5, y=0.23))
        self.session.add(vertex)
        self.session.commit()
        
        self.assertEqual(len(self.session.query(AreaVertex).all()), 1,
            "Wrong number of entries.")
        self.assertEqual(self.session.query(AreaVertex).first().coordinate, Coordinate(1.5, 0.23),
            "Wrong vertex retrieved.")
        self.assertTrue(self.session.query(AreaVertex).filter(AreaVertex.coordinate == Coordinate(1.5, 0.23)).first() is vertex,
            "Failed to filter by coordinate.")
        self.assertEqual(len(self.session.query(AreaVertex).filter(AreaVertex.coordinate == Coordinate(1.5, 1.5)).all()), 0,
            "Failed to filter by nonexistant property.")

    def test_multiple_unique_entries(self):
        n_max_vertices = 100
        n_vertices_for_session = [randint(1, n_max_vertices) for i in range(self.SESSIONS)]
        coordinates = [[Coordinate(uniform(1, 100), uniform(1, 100)) for i in range(j)] for j in n_vertices_for_session]
        vertices = [[AreaVertex(session_id=i, vertex_no=j, coordinate=coordinates[i][j]) for j in range(n_vertices_for_session[i])] for i in range(self.SESSIONS)]
        for session_vertices in vertices:
            for vertex in session_vertices:
                self.session.add(vertex)
        self.session.commit()

        vertices_in_database = self.session.query(AreaVertex).\
            order_by(AreaVertex.session_id, AreaVertex.vertex_no).all()
        self.assertEqual(len(vertices_in_database), sum(n_vertices_for_session),
            "Incorrect number of entries saved in database.")
        for session_id in range(self.SESSIONS):
            with self.subTest(i=session_id):
                session_vertices = self.session.query(AreaVertex).filter(AreaVertex.session_id == session_id).all()
                self.assertEqual(len(session_vertices), n_vertices_for_session[session_id],
                    "Incorrect number of vertices retrieved for session.")
                for i in range(n_vertices_for_session[session_id]):
                    with self.subTest(i=i):
                        self.assertTrue(vertices[session_id][i] is session_vertices[i],
                            "Retrieved vertex is not the same object as created vertex.")
        self.assertEqual(len(self.session.query(AreaVertex).\
            filter(AreaVertex.coordinate == Coordinate(-1, -1)).all()), 0,
            "Found nonexistant vertex.")

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

class ImageTester(unittest.TestCase):
    
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
        image = Image(
            session_id=randint(1, self.SESSIONS),
            time_taken=randint(100000, 200000), 
            width=480, height=360, type="IR",
            up_left=Coordinate(1, 5),
            up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1),
            down_left=Coordinate(1, 1),
            file_path="images/1.jpg"
        )
        self.session.add(image)
        self.session.commit()
        
        self.assertEqual(len(self.session.query(Image).all()), 1,
            "Wrong number of entries.")
        self.assertEqual(self.session.query(Image.width).first()[0], 480,
            "Wrong width retrieved.")
        self.assertTrue(self.session.query(Image).filter(Image.height == 360).first() is image,
            "Failed to filter by coordinate.")
        self.assertEqual(len(self.session.query(Image).filter(Image.type == "LASERBEAM").all()), 0,
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
        file_path = ["{}.jpg".format(i) for i in range(n_images)]

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
            file_path=file_path[i]
        ) for i in range(n_images)]
        for image in images:
            self.session.add(image)
        self.session.commit()

        self.assertEqual(len(self.session.query(Image).all()), n_images,
            "Incorrect number of entries saved in database.")
        for session_id in range(self.SESSIONS):
            with self.subTest(i=session_id):
                session_images = self.session.query(Image).filter(Image.session_id == session_id).all()
                self.assertEqual(len(session_images), session.count(session_id),
                    "Incorrect number of images retrieved for session.")
        images_in_database = self.session.query(Image).order_by(Image.id).all()
        for i in range(n_images):
            with self.subTest(i=i):
                self.assertTrue(images_in_database[i] is images[i],
                    "Retrieved Image is not the same object as inserted Image.")
        self.assertEqual(len(self.session.query(Image).\
            filter(Image.width == 0).all()), 0,
            "Found nonexistant vertex.")

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
            file_path="1.jpg"
        ))
        check_invalid(Image(
            session_id=1,
            width=240, height=360, type="IR",
            up_left=Coordinate(1, 5), up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1), down_left=Coordinate(1, 1),
            file_path="1.jpg"
        ))
        check_invalid(Image(
            session_id=1, time_taken=100000,
            height=360, type="IR",
            up_left=Coordinate(1, 5), up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1), down_left=Coordinate(1, 1),
            file_path="1.jpg"
        ))
        check_invalid(Image(
            session_id=1, time_taken=100000,
            width=240, type="IR",
            up_left=Coordinate(1, 5), up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1), down_left=Coordinate(1, 1),
            file_path="1.jpg"
        ))
        check_invalid(Image(
            session_id=1, time_taken=100000,
            width=240, height=360,
            up_left=Coordinate(1, 5), up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1), down_left=Coordinate(1, 1),
            file_path="1.jpg"
        ))
        check_invalid(Image(
            session_id=1, time_taken=100000,
            width=240, height=360, type="IR",
            up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1), down_left=Coordinate(1, 1),
            file_path="1.jpg"
        ))
        check_invalid(Image(
            session_id=1, time_taken=100000,
            width=240, height=360, type="IR",
            up_left=Coordinate(1, 5),
            down_right=Coordinate(5, 1), down_left=Coordinate(1, 1),
            file_path="1.jpg"
        ))
        check_invalid(Image(
            session_id=1, time_taken=100000,
            width=240, height=360, type="IR",
            up_left=Coordinate(1, 5), up_right=Coordinate(5, 5),
            down_left=Coordinate(1, 1),
            file_path="1.jpg"
        ))
        check_invalid(Image(
            session_id=1, time_taken=100000,
            width=240, height=360, type="IR",
            up_left=Coordinate(1, 5), up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1),
            file_path="1.jpg"
        ))
        check_invalid(Image(
            session_id=1, time_taken=100000,
            width=240, height=360, type="IR",
            up_left=Coordinate(1, 5), up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1), down_left=Coordinate(1, 1),
        ))

class SessionRelationTester(unittest.TestCase):
    def setUp(self):
        seed(123)   # Avoid flaky tests by using the same seed every time.
        self.db = get_test_database()
        self.session = self.db.get_session()

    def tearDown(self):
        self.db.release_session()

    def testSessionClientRelation(self):
        session = UserSession(id=1, start_time=100, end_time=200, drone_mode="AUTO")
        client = Client(session_id=session.id,
            up_left=Coordinate(1, 5), up_right=Coordinate(5, 5),
            down_right=Coordinate(5, 1), down_left=Coordinate(1, 1))
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


if __name__ == "__main__":
    unittest.main()