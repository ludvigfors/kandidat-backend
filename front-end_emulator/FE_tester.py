import zmq
import time
import json
from threading import Thread
context = zmq.Context()

"""
zmq.REQ: Starts sending messages
zmq.REP: Starts with receiving messages
"""
pub_socket_url = "tcp://localhost:4570"
sub_socket_url = "tcp://localhost:4571"
req_socket_url = "tcp://localhost:4572"


class PubThread(Thread):

    def __init__(self):
        super().__init__()
        self.pub_socket = context.socket(zmq.REQ)
        self.req_socket = context.socket(zmq.REQ)
        self.pub_socket.connect(pub_socket_url)
        self.req_socket.connect(req_socket_url)

    def run(self):
        # Simulating frontend making a series of calls

        # Connect to backend
        req1 = {}



        # Set area


        # Request point of interest




class SubThread(Thread):
    def __init__(self):
        super().__init__()
        self.sub_socket = context.socket(zmq.REP)
        self.sub_socket.connect(sub_socket_url)

    def run(self):
        while True:
            message = self.sub_socket.recv_json()
            print("Received message", message)
            self.sub_socket.send_json(json.dumps({"msg":"ack"}))

            #if message == "notify":
                # Request image by id


ppthread = PubThread()
ppthread.start()
subscriber_thread = SubThread()
subscriber_thread.start()



