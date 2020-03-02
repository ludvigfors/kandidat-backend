from serversocket import socket
from database import Image, session
from threading import Thread, Event
import time
import json


class MyThread(Thread):

    def __init__(self):
        super().__init__()
        self.image_queue = []
        self.DELAY = 40
        self.count = 0

    def run(self):
        while True:
            if len(self.image_queue) > 0:
                self.countdown() # Simulate drone flying to location
                print("Got picture")
                new_pic(self.image_queue.pop(0))

    def add_image(self, image):
        self.image_queue.append(image)

    def countdown(self):
        self.count = self.DELAY
        while self.count > 0:
            time.sleep(1)
            self.count -= 1


    def next_image_eta(self):
        return self.count


thread = MyThread()
thread.start()


def init():
    coord = {
                "up_left":
                    {
                        "lat":58.123456,
                        "long":16.12345613
             },
                 "up_right":
                     {
                         "lat":58.123456,
                         "long":16.12345618
                     },
                 "down_left":
                     {
                         "lat":58.123456,
                         "long":16.12345623
                     },
                 "down_right":
                     {"lat":58.123456,
                      "long":16.12345628
                      },
                 "center":
                     {
                         "lat":58.123456,
                         "long":16.123456
                     }
             }
    testFilePath = "/home/ludvig/Desktop/RDS_emulator/images/testimage.jpg"
    image = Image(coord, testFilePath)
    session.add(image)
    session.commit()


def new_pic(image):
    "Called when a new picture is taken, send this to the client that wanted it."
    print(image)
    res = {
        "fcn":"new_pic",
        "arg": {
            "drone_id":"one",
            "type":"rgb",
            "force_que_id":0,
            "coordinates":
                {
                    "up_left":
                        {
                            "lat": 58.123456,
                            "long": 16.12345613
                        },
                    "up_right":
                        {
                            "lat": 58.123456,
                            "long": 16.12345618
                        },
                    "down_left":
                        {
                            "lat": 58.123456,
                            "long": 16.12345623
                        },
                    "down_right":
                        {"lat": 58.123456,
                         "long": 16.12345628
                         },
                    "center":
                        {
                            "lat": 58.123456,
                            "long": 16.123456
                        }
                }
        }
    }

    socket.send_json(json.dumps(res))



def add_poi(arguments):
    """Gets corner coordinates from client, force """

    coordinates = arguments["coordinates"]
    image = session.query(Image).filter_by(coordinates=coordinates).first()
    thread.add_image(image)
    print("Image added to queue")
    return "hej"


def get_info():
    """Returns info on connected drones, for now"""
    pass


def set_area():
    pass


def clear_que():
    """Returns info on connected drones, for now"""
    pass


def eta():
    """Returns the time (in seconds) until next picture"""

    res = {
        "fcn": "ack",
        "arg": "que_ETA",
        "arg2": str(thread.next_image_eta())
    }
    print("ETA", res)
    return res
