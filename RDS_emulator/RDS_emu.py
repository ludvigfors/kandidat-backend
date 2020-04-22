import platform

import numpy
import os
from RDS_emulator.database import Image, create_engine, sessionmaker, session_scope
from threading import Thread
from PIL import Image as PIL_image
import time
import json
import zmq
from helper_functions import get_path_from_root

context = zmq.Context()

class DroneThread(Thread):
    """
    Simulates a drone flying for FLYING_TIME seconds and then takes an image.
    """

    def __init__(self):
        super().__init__()
        self.image_queue = []
        self.FLYING_TIME = 1
        self.count = 0
        self.new_image = False
        self.running = True
        self.mode = "MAN"
        self.stuff_is_changing = False

    def run(self):
        while self.running:
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

    def stop(self):
        self.running = False

    def set_mode(self, mode):
        self.mode = mode

    def get_mode(self):
        return self.mode

    def start_change(self):
        self.stuff_is_changing = True

    def stop_change(self):
        self.stuff_is_changing = False

    def is_changing(self):
        return self.stuff_is_changing


class IMMPubThread(Thread):
    """Simulates RDS Publish link"""

    def __init__(self, socket_url, drone):
        super().__init__()
        self.socket = context.socket(zmq.REQ)
        self.socket.bind(socket_url)
        self.drone_thread = drone
        self.running = True

    def run(self):
        while self.running:
            if self.drone_thread.new_image:
                self.new_pic(self.drone_thread.pop_first_image())
                response = self.socket.recv_json()
                print(response)
        i = 0

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

    def stop(self):
        self.running = False


class IMMSubThread(Thread):
    """Simulates RDS-Subscribe link"""

    def __init__(self, socket_url, drone):
        super().__init__()
        self.socket = context.socket(zmq.REP)
        self.socket.bind(socket_url)
        self.drone_thread = drone
        self.running = True

    def run(self):
        while self.running:
            try:
                request = json.loads(self.socket.recv_json())
                if request["fcn"] == "add_poi":
                    self.socket.send_json(self.add_poi(request["arg"]))
                else:
                    self.socket.send_json(json.dumps({"msg": "nothing happened"}))
            except:
                pass

    def add_poi(self, arguments):
        """Gets corner coordinates from client"""
        coordinates = arguments["coordinates"]
        # Maybe add a wait here to make it threadsafe
        with session_scope() as session:
            if not self.drone_thread.get_mode() == "AUTO":
                image = session.query(Image).filter_by(coordinates=coordinates).first()
                if image is not None:
                    self.drone_thread.add_image_to_queue(image)
                    # print("Image added to queue")
                    return {"msg": "Image added to queue"}
                else:
                    return {"msg":"Something went wrong"}

    def stop(self):
        context.destroy()
        self.running = False


class IMMRepThread(Thread):
    """Simulates the Reply-link (INFO-link)"""
    def __init__(self, socket_url, drone):
        super().__init__()
        self.socket = context.socket(zmq.REP)
        self.socket.bind(socket_url)
        self.drone_thread = drone
        self.running = True

    def run(self):
        while self.running:
            request = json.loads(self.socket.recv_json())
            self.drone_thread.start_change()
            if request["fcn"] == "queue_eta":
                self.socket.send_json(self.eta())
            elif request["fcn"] == "set_mode":
                self.socket.send_json(self.set_mode(request))
            self.drone_thread.stop_change()

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
            "arg2": str(self.drone_thread.next_image_eta())
        }
        # print("ETA", res)
        return res

    def stop(self):
        context.destroy()
        self.running = False

    def set_mode(self, request):
        self.drone_thread.set_mode(request["arg"]["mode"])
        if request["arg"]["mode"] == "AUTO":
            self.add_auto_images_to_queue() # So images will be sent continously.
        return {"msg": "mode set"}

    def add_auto_images_to_queue(self):
        with session_scope() as session:
            auto_images = session.query(Image).filter_by(mode="AUTO").all()
            for image in auto_images:
                self.drone_thread.add_image_to_queue(image)
            i = 0














