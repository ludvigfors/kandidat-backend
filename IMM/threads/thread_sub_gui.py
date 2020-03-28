from IMM.IMM_thread_init import context, zmq, gui_sub_socket_url, RDS_pub_socket_url
from threading import Thread
import json
import random


class GuiSubThread(Thread):
    """This thread subscribes to the gui and handle POI-requests"""  # This thread might be overkill

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

