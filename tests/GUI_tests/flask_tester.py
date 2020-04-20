import unittest
import json, os

from RDS_emulator.RDS_app import RDSThreadHandler
from helper_functions import get_path_from_root
from IMM.IMM_app import *
from IMM_database.database import use_test_database
from  RDS_emulator.database import use_test_database_rds, Image, session_scope


class TestFlask(unittest.TestCase):
    def setUp(self):
        #app.config['TESTING'] = True
        #app.config['WTF_CSRF_ENABLED'] = False
        #app.config['DEBUG'] = False
        #self.client = socketio.test_client(app)
        #self.rds_handler = RDSThreadHandler()
        #self.rds_handler.start_threads()
        use_test_database(False)
        #thread_handler.start_threads()
        #use_test_database_rds(False)
        #init_db_and_add_image()
        pass

    def tearDown(self):
        thread_handler.stop_threads()
        #self.rds_handler.stop_threads()

    def test_unit_connect(self):
        print(on_connect())

    def test_connect(self):
        client = socketio.test_client(app)
        self.assertTrue(client.is_connected())
        recieved = client.get_received()
        self.assertTrue("CONNECTED TO BACKEND1", recieved[0]["args"])

    def test_request_view(self):
        client = socketio.test_client(app)
        self.assertTrue(client.is_connected())

        #test request_view
        request = {
            "fcn": "request_POI",
            "arg":
                {
                    # "client_id": 1, # Not implemented yet
                    "prio": False,
                    "coordinates": {
                        "up_left":
                            {
                                "lat": 59,
                                "long": 16
                            },
                        "up_right":
                            {
                                "lat": 58,
                                "long": 16
                            },
                        "down_left":
                            {
                                "lat": 58,
                                "long": 16
                            },
                        "down_right":
                            {"lat": 58,
                             "long": 16
                             },
                        "center":
                            {
                                "lat": 58,
                                "long": 16
                            }
                    }

                }
        }

        client.emit("request_view", request)
        recieved = client.get_received()
        self.assertTrue(request, recieved[0]["args"])

    """
    def test_request_image(self):
        req3 = {
            "fcn": "request_POI",
            "arg":
                {
                    # "client_id": 1, # Not implemented yet
                    "prio": False,
                    "coordinates": {
                        "up_left":
                            {
                                "lat": 59,
                                "long": 16
                            },
                        "up_right":
                            {
                                "lat": 58,
                                "long": 16
                            },
                        "down_left":
                            {
                                "lat": 58,
                                "long": 16
                            },
                        "down_right":
                            {"lat": 58,
                             "long": 16
                             },
                        "center":
                            {
                                "lat": 58,
                                "long": 16
                            }
                    }

                }
        }
        url = "http://localhost:8080"
        resp = self.app.post(url+"/request_image", data=json.dumps(req3))



def init_db_and_add_image():
    Inserts a test image into the IMM_database

    with session_scope() as session:

        coord = {
            "up_left":
                {
                    "lat": 59,
                    "long": 16
                },
            "up_right":
                {
                    "lat": 58,
                    "long": 16
                },
            "down_left":
                {
                    "lat": 58,
                    "long": 16
                },
            "down_right":
                {"lat": 58,
                 "long": 16
                 },
            "center":
                {
                    "lat": 58,
                    "long": 16
                }
        }
        testFilePath = get_path_from_root("/RDS_emulator/images/testimage.jpg")
        image = Image(coord, testFilePath)
        session.add(image)
        session.commit()

        """
if __name__ == "__main__":
    unittest.main()
