import unittest
from threading import Thread
from IMM.IMM_app import *
from IMM_database.database import use_test_database
from  RDS_emulator.RDS_app import RDSThreadHandler
from RDS_emulator.database import use_test_database_rds, session_scope, Image
from helper_functions import get_path_from_root


class TestFlask(unittest.TestCase):
    def setUp(self):
        #self.client = socketio.test_client(app)
        self.rds_handler = RDSThreadHandler()
        self.rds_handler.start_threads()
        use_test_database(False)
        use_test_database_rds(False)
        init_db_and_add_images()
        pass

    def tearDown(self):
        pass
        #thread_handler.stop_threads()
        # self.rds_handler.stop_threads()

    #def test_unit_connect(self):
     #   print(on_connect())

    def test_request_view(self):
        client = socketio.test_client(app)
        self.assertTrue(client.is_connected())

        mode_req = {
            "fcn":"set_mode",
            "arg": {
                "mode": "AUTO",
                "zoom": {
                    "zoomcoordinates":"none"
                }
            }
        }
        client.emit("set_mode", mode_req)
        recieved = client.get_received()
        self.assertTrue(mode_req, recieved[0]["args"])

        """
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


def init_db_and_add_images():
    """Inserts a test image into the IMM_database"""

    def insert_man_images():
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
            image = Image(coord, testFilePath, "MAN")
            session.add(image)

    def insert_auto_images():
        with session_scope() as session:

            image1_coords = {
                "up_left":
                    {
                        "lat": 59.812507,
                        "long": 17.656431
                    },
                "up_right":
                    {
                        "lat": 59.811107,
                        "long": 17.656431
                    },
                "down_left":
                    {
                        "lat": 59.812507,
                        "long": 17.654431
                    },
                "down_right":
                    {
                        "lat": 59.811107,
                        "long": 17.654431
                    },
                "center":
                    {
                        "lat": 59.811807,
                        "long": 17.655431
                    }
            }

            image2_coords = {
                "up_left":
                    {
                        "lat": 59.812513,
                        "long": 17.657309
                    },
                "up_right":
                    {
                        "lat": 59.811113,
                        "long": 17.657309
                    },
                "down_left":
                    {
                        "lat": 59.812513,
                        "long": 17.655309
                    },
                "down_right":
                    {
                        "lat": 59.811113,
                        "long": 17.655309
                    },
                "center":
                    {
                        "lat": 59.811813,
                        "long": 17.656309
                    }
            }

            image3_coords = {
                "up_left":
                    {
                        "lat": 59.812532,
                        "long": 17.658139
                    },
                "up_right":
                    {
                        "lat": 59.811132,
                        "long": 17.658139
                    },
                "down_left":
                    {
                        "lat": 59.812532,
                        "long": 17.656139
                    },
                "down_right":
                    {
                        "lat": 59.811132,
                        "long": 17.656139
                    },
                "center":
                    {
                        "lat": 59.811832,
                        "long": 17.657139
                    }
            }

            image4_coords = {
                "up_left":
                    {
                        "lat": 59.812553,
                        "long": 17.659012
                    },
                "up_right":
                    {
                        "lat": 59.811107,
                        "long": 17.659012
                    },
                "down_left":
                    {
                        "lat": 59.812553,
                        "long": 17.657012
                    },
                "down_right":
                    {
                        "lat": 59.811153,
                        "long": 17.657012
                    },
                "center":
                    {
                        "lat": 59.811853,
                        "long": 17.658012
                    }
            }

            img_1_path = get_path_from_root("/RDS_emulator/AUTO_images/auto_sequence_test_images/DJI_im1.JPG")
            img_2_path = get_path_from_root("/RDS_emulator/AUTO_images/auto_sequence_test_images/DJI_im2.JPG")
            img_3_path = get_path_from_root("/RDS_emulator/AUTO_images/auto_sequence_test_images/DJI_im3.JPG")
            img_4_path = get_path_from_root("/RDS_emulator/AUTO_images/auto_sequence_test_images/DJI_im4.JPG")

            image_1 = Image(image1_coords, img_1_path, "AUTO")
            image_2 = Image(image2_coords, img_2_path, "AUTO")
            image_3 = Image(image3_coords, img_3_path, "AUTO")
            image_4 = Image(image4_coords, img_4_path, "AUTO")

            session.add(image_1)
            session.add(image_2)
            session.add(image_3)
            session.add(image_4)

    # insert_man_images()
    insert_auto_images()



if __name__ == "__main__":
    unittest.main()
