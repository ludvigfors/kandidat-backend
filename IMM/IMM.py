import zmq
import time
import json
from threading import Thread
context = zmq.Context()

RDS_pub_socket_url = "tcp://localhost:5570"
RDS_sub_socket_url = "tcp://localhost:5571"
RDS_req_socket_url = "tcp://localhost:5572"

FE_pub_socket_url = "tcp://localhost:4570"
FE_sub_socket_url = "tcp://localhost:4571"
FE_resp_socket_url = "tcp://localhost:4572"

"""
zmq.REQ: Starts sending messages
zmq.REP: Starts with receiving messages
"""

class FrontendSubThread(Thread):

    def __init__(self):
        super().__init__()
        self.FE_sub_socket = context.socket(zmq.REP)
        self.RDS_pub_socket = context.socket(zmq.REQ)
        self.FE_sub_socket.connect(FE_sub_socket_url)
        self.RDS_pub_socket.connect(RDS_pub_socket_url)

    def run(self):
        pass


class RDSSubThread(Thread):
    def __init__(self):
        super().__init__()
        self.RDS_sub_socket = context.socket(zmq.REP)
        self.FE_pub_socket = context.socket(zmq.REQ)
        self.RDS_sub_socket.connect(RDS_sub_socket_url)
        self.FE_pub_socket.connect(FE_pub_socket_url)

    def run(self):
        while True:
            resp = self.sub_socket.recv_json()
            print("New message", resp)
            self.sub_socket.send_json(json.dumps({"msg":"ack"}))


class ReqRespThread(Thread):
    def __init__(self):
        super().__init__()
        self.FE_resp_socket = context.socket(zmq.REP)
        self.RDS_req_socket = context.socket(zmq.REQ)
        self.FE_resp_socket.connect(FE_resp_socket_url)
        self.RDS_req_socket.connect(RDS_req_socket_url)

    def run(self):
        while True:
            resp = self.sub_socket.recv_json()
            print("New message", resp)
            self.sub_socket.send_json(json.dumps({"msg":"ack"}))


ppthread = FrontendPubThread()
ppthread.start()
subscriber_thread = FrontendSubThread()
subscriber_thread.start()



