import unittest
from random import randint, seed

from database import UserSession
from database import get_test_database

class UserSessionTester(unittest.TestCase):
    
    def setUp(self):
        seed(123)
        self.session = get_test_database().Session()

    def tearDown(self):
        pass

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


if __name__ == "__main__":
    unittest.main()