import zmq
import uuid
import random
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


class GuiSubThread(Thread):

    def __init__(self):
        super().__init__()
        self.Gui_sub_socket = context.socket(zmq.REP)
        self.RDS_pub_socket = context.socket(zmq.REQ)
        self.Gui_sub_socket.connect(FE_sub_socket_url)
        self.RDS_pub_socket.connect(RDS_pub_socket_url)

    def run(self):
        while True:
            request = self.Gui_sub_socket.recv_json()
            if request["fcn"] == "request_POI":
                self.request_poi(request["arg"])

    def request_poi(self, poi):
        request = {"fcn": "add_poi"}
        request_args = {"client_id": 1, "force_que_id": 0}
        if poi["prio"]:
            request_args["force_que_id"] = random.randint()  # TODO: Ganrante that the number is unique

        request_args["coordinates"] = poi["coordinates"]
        request["arg"] = request_args
        self.send_to_rds(request)

    def send_to_rds(self, args):
        self.RDS_pub_socket.send_json(json.dumps(args))
        resp = self.RDS_pub_socket.recv()
        print("Response (ack/nack)", resp)


class RDSSubThread(Thread):
    def __init__(self):
        super().__init__()
        self.RDS_sub_socket = context.socket(zmq.REP)
        self.Gui_pub_socket = context.socket(zmq.REQ)
        self.RDS_sub_socket.connect(RDS_sub_socket_url)
        self.Gui_pub_socket.connect(FE_pub_socket_url)

    def run(self):
        while True:
            resp = self.RDS_sub_socket.recv_json()
            print("New message", resp)
            self.RDS_sub_socket.send_json(json.dumps({"msg":"ack"}))

            # TODO: Save to database

            self.notify_gui()

    def notify_gui(self):
        req = {"fcn": "new_pic", "arg":{"image_id": 1}}  # This is not final
        self.Gui_pub_socket.send_json(json.dumps(req))
        resp = self.Gui_pub_socket.recv_json()
        print("Resp:", resp)


class ReqRespThread(Thread):
    def __init__(self):
        super().__init__()
        self.Gui_resp_socket = context.socket(zmq.REP)
        self.RDS_req_socket = context.socket(zmq.REQ)
        self.Gui_resp_socket.connect(FE_resp_socket_url)
        self.RDS_req_socket.connect(RDS_req_socket_url)

    def run(self):
       pass

