import zmq
import time
import json
from threading import Thread
context = zmq.Context()


class PushPullThread(Thread):

    def __init__(self):
        super().__init__()
        self.client_pub_socket = context.socket(zmq.REQ)
        self.client_req_socket = context.socket(zmq.REQ)
        self.client_pub_socket.connect("tcp://localhost:5570")
        self.client_req_socket.connect("tcp://localhost:5572")

    def run(self):
        # Simulating a series of calls
        print("Calling add_poi")

        request1 = {
            "fcn": "add_poi",
            "arg":
                {
                    "client_id": 1,
                    "force_que_id": 0,
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

        self.client_pub_socket.send_json(json.dumps(request1))
        message = self.client_pub_socket.recv()
        print(message)

        request2 = {
            "fcn": "queue_eta",
        }
        print("Calling queue_eta")
        self.client_req_socket.send_json(json.dumps(request2))
        message2 = self.client_req_socket.recv()
        print(message2)

        time.sleep(2) # To test if you can get the queue_eta.
        print("Calling queue_eta after 2 seconds sleep")

        self.client_req_socket.send_json(json.dumps(request2))
        message3 = self.client_req_socket.recv()
        print(message3)


class SubscriberThread(Thread):
    def __init__(self):
        super().__init__()
        self.sub_socket = context.socket(zmq.REP)
        self.sub_socket.connect("tcp://localhost:5571")

    def run(self):
        while True:
            resp = self.sub_socket.recv_json()
            print("New message", resp)
            self.sub_socket.send_json(json.dumps({"msg":"ack"}))


ppthread = PushPullThread()
ppthread.start()
subscriber_thread = SubscriberThread()
subscriber_thread.start()


