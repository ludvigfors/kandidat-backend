import zmq
import time
import json
from threading import Thread
context = zmq.Context()


class PubThread(Thread):

    def __init__(self):
        super().__init__()
        self.client_pub_socket = context.socket(zmq.REQ)
        self.client_req_socket = context.socket(zmq.REQ)
        self.client_pub_socket.connect("tcp://localhost:5570")
        self.client_req_socket.connect("tcp://localhost:5572")

    def run(self):
        # Simulating a series of calls

        # Connect to backend
        print("Calling add_poi")


        # Set area


        # Request point of interest




class SubThread(Thread):
    def __init__(self):
        super().__init__()
        self.sub_socket = context.socket(zmq.REP)
        self.sub_socket.connect("tcp://localhost:5571")

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



