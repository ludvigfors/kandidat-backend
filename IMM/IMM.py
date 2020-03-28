import zmq
import time
import json
from threading import Thread
context = zmq.Context()



class FrontendPubThread(Thread):

    def __init__(self):
        super().__init__()
        self.client_pub_socket = context.socket(zmq.REQ)
        self.client_req_socket = context.socket(zmq.REQ)
        self.client_pub_socket.connect("tcp://localhost:5570")
        self.client_req_socket.connect("tcp://localhost:5572")

    def run(self):
        pass


class FrontendSubThread(Thread):
    def __init__(self):
        super().__init__()
        self.sub_socket = context.socket(zmq.REP)
        self.sub_socket.connect("tcp://localhost:5571")

    def run(self):
        while True:
            resp = self.sub_socket.recv_json()
            print("New message", resp)
            self.sub_socket.send_json(json.dumps({"msg":"ack"}))


ppthread = FrontendPubThread()
ppthread.start()
subscriber_thread = FrontendSubThread()
subscriber_thread.start()



