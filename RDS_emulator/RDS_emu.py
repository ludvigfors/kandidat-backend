import numpy

from RDS_emulator.database import Image, session
from threading import Thread
from PIL import Image as PIL_image
import time
import json
import zmq

context = zmq.Context()

class DroneThread(Thread):
    """
    Simulates a drone flying for FLYING_TIME seconds and then takes an image.
    """

    def __init__(self):
        super().__init__()
        self.image_queue = []
        self.FLYING_TIME = 4
        self.count = 0
        self.new_image = False

    def run(self):
        while True:
            if not self.new_image and len(self.image_queue) > 0:
                self.countdown() # Simulate drone flying to location
                # print("Image arrived")
                self.new_image = True

    def add_image_to_queue(self, image):
        self.image_queue.append(image)

    def pop_first_image(self):
        self.new_image = False
        return self.image_queue.pop(0)

    def has_new_image(self):
        return self.new_image

    def countdown(self):
        self.count = self.FLYING_TIME
        while self.count > 0:
            time.sleep(1)
            self.count -= 1

    def next_image_eta(self):
        return self.count

drone_thread = DroneThread()
drone_thread.start()


class IMMPubThread(Thread):
    """Simulates RDS Publish link"""

    def __init__(self, socket_url):
        super().__init__()
        self.socket = context.socket(zmq.REQ)
        self.socket.bind(socket_url)

    def run(self):
        while True:
            if drone_thread.new_image:
                self.new_pic(drone_thread.pop_first_image())
                response = self.socket.recv_json()
                # print(response)

    def new_pic(self, image):
        "Called when a new picture is taken, send this to the client that wanted it."

        A = numpy.array(PIL_image.open(image.image_path))
        message = {
            "fcn": "new_pic",
            "arg": {
                "drone_id": "one",
                "type": "rgb",
                "force_que_id": 0,
                "coordinates": image.coordinates
            }
        }
        self.send_array(message, A)

    def send_array(self, metadata, A, flags=0, copy=True, track=False):
        image_md = dict(
            dtype=str(A.dtype),
            shape=A.shape,
        )
        
        metadata["image_md"] = image_md
        
        self.socket.send_json(metadata, flags | zmq.SNDMORE)
        self.socket.send(A, flags, copy=copy, track=track)


class IMMSubThread(Thread):
    """Simulates RDS-Subscribe link"""

    def __init__(self, socket_url):
        super().__init__()
        self.socket = context.socket(zmq.REP)
        self.socket.bind(socket_url)

    def run(self):
        while True:
            request = json.loads(self.socket.recv_json())
            if request["fcn"] == "add_poi":
                self.socket.send_json(self.add_poi(request["arg"]))

            else:
                self.socket.send_json(json.dumps({"msg": "nothing happened"}))

    def add_poi(self, arguments):
        """Gets corner coordinates from client"""
        coordinates = arguments["coordinates"]
        image = session.query(Image).filter_by(coordinates=coordinates).first()
        if image is not None:
            drone_thread.add_image_to_queue(image)
            # print("Image added to queue")
            return {"msg": "Image added to queue"}
        else:
            return {"msg":"Something went wrong"}


class IMMRepThread(Thread):
    """Simulates the Reply-link (INFO-link)"""
    def __init__(self, socket_url):
        super().__init__()
        self.socket = context.socket(zmq.REP)
        self.socket.bind(socket_url)

    def run(self):
        while True:
            request = json.loads(self.socket.recv_json())
            if request["fcn"] == "queue_eta":
                self.socket.send_json(self.eta())

    def get_info(self):
        """Returns info on connected drones, for now"""
        pass

    def set_area(self):
        pass

    def clear_que(self):
        """Returns info on connected drones, for now"""
        pass

    def eta(self):
        """Returns the time (in seconds) until next picture"""

        res = {
            "fcn": "ack",
            "arg": "que_ETA",
            "arg2": str(drone_thread.next_image_eta())
        }
        # print("ETA", res)
        return res


def init_db_and_add_image():
    """Inserts a test image into the database"""
    coord = {
                "up_left":
                    {
                        "lat":59,
                        "long":16
             },
                 "up_right":
                     {
                         "lat":58,
                         "long":16
                     },
                 "down_left":
                     {
                         "lat":58,
                         "long":16
                     },
                 "down_right":
                     {"lat":58,
                      "long":16
                      },
                 "center":
                     {
                         "lat":58,
                         "long":16
                     }
             }
    testFilePath = "/home/ludvig/Desktop/back-end/RDS_emulator/images/testimage.jpg"
    image = Image(coord, testFilePath)
    session.add(image)
    session.commit()











