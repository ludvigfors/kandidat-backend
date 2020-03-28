import zmq
import uuid
import random
import json
from threading import Thread
context = zmq.Context()

RDS_pub_socket_url = "tcp://localhost:5570"
RDS_sub_socket_url = "tcp://localhost:5571"
RDS_req_socket_url = "tcp://localhost:5572"

giu_pub_socket_url = "tcp://*:4570"
gui_sub_socket_url = "tcp://*:4571"
gui_resp_socket_url = "tcp://*:4572"

"""
zmq.REQ: Start by sending messages
zmq.REP: Start by receiving messages
"""


class GuiSubThread(Thread):

    def __init__(self):
        super().__init__()
        self.gui_sub_socket = context.socket(zmq.REP)
        self.RDS_pub_socket = context.socket(zmq.REQ)
        self.gui_sub_socket.bind(gui_sub_socket_url)
        self.RDS_pub_socket.connect(RDS_pub_socket_url)

    def run(self):
        while True:
            request = json.loads(self.gui_sub_socket.recv_json())
            if request["fcn"] == "request_POI":
                self.gui_sub_socket.send_json(self.request_poi(request["arg"]))

            else:
                self.gui_sub_socket.send_json(json.dumps({"msg": "nothing happened"}))

    def request_poi(self, poi):
        request = {"fcn": "add_poi"}
        request_args = {"client_id": 1, "force_que_id": 0}
        if poi["prio"]:
            request_args["force_que_id"] = random.randint()  # TODO: Garantee that the number is unique

        request_args["coordinates"] = poi["coordinates"]
        request["arg"] = request_args
        self.send_to_rds(request)
        return {"msg":"Poi added"}

    def send_to_rds(self, args):
        self.RDS_pub_socket.send_json(json.dumps(args))
        resp = self.RDS_pub_socket.recv()
        # print("Response (ack/nack)", resp)


class RDSSubThread(Thread):
    def __init__(self):
        super().__init__()
        self.RDS_sub_socket = context.socket(zmq.REP)
        self.gui_pub_socket = context.socket(zmq.REQ)
        self.RDS_sub_socket.connect(RDS_sub_socket_url)
        self.gui_pub_socket.bind(giu_pub_socket_url)

    def run(self):
        while True:
            new_pic = self.RDS_sub_socket.recv_json()
            # print("New pic", new_pic)
            self.RDS_sub_socket.send_json(json.dumps({"msg": "ack"}))
            self.save_to_database(new_pic)
            self.notify_gui()

    def notify_gui(self):
        msg = {"fcn": "new_pic", "arg":{"image_id": 1}}  # This notify message will change later
        self.gui_pub_socket.send_json(json.dumps(msg))
        resp = self.gui_pub_socket.recv_json()
        # print("notify gui response:", resp)

    def save_to_database(self, new_pic):
        # TODO: Save new pic to database here
        pass


class ReqRespThread(Thread):
    def __init__(self):
        super().__init__()
        self.gui_resp_socket = context.socket(zmq.REP)
        self.RDS_req_socket = context.socket(zmq.REQ)
        self.gui_resp_socket.bind(gui_resp_socket_url)
        self.RDS_req_socket.connect(RDS_req_socket_url)

    def run(self):
        while True:
            request = json.loads(self.gui_resp_socket.recv_json())

            if request["fcn"] == "connect":
                self.gui_resp_socket.send_json(self.connect())

            elif request["fcn"] == "set_area":
                self.gui_resp_socket.send_json(self.set_area())

            elif request["fcn"] == "get_info":
                self.gui_resp_socket.send_json(self.get_info())

            elif request["fcn"] == "set_mode":
                self.gui_resp_socket.send_json(self.set_mode())

            elif request["fcn"] == "clear_que":
                self.gui_resp_socket.send_json(self.clear_queue())

            elif request["fcn"] == "que_ETA":
                self.gui_resp_socket.send_json(self.queue_eta())

            elif request["fcn"] == "quit":
                self.gui_resp_socket.send_json(self.disconnect())

            else:
                self.gui_resp_socket.send_json(json.dumps({"msg": "nothing happened"}))

    def connect(self):
        # TODO: Implement this
        pass

    def set_area(self):
        # TODO: Implement this
        pass

    def get_info(self):
        # TODO: Implement this
        pass

    def disconnect(self):
        # TODO: Implement this
        pass

    def set_mode(self):
        # TODO: Implement this
        pass

    def clear_queue(self):
        # TODO: Implement this
        pass

    def queue_eta(self):
        # TODO: Implement this
        pass
