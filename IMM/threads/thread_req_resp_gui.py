from IMM.IMM_thread_config import context, zmq, gui_resp_socket_url, RDS_req_socket_url, gui_sub_socket_url, RDS_pub_socket_url
from threading import Thread
import json
import random


class GuiReqRespThread(Thread):
    """This thread handles the requests sent by the gui.
        It will contact the RDS for the requested action"""

    def __init__(self):
        super().__init__()
        self.gui_resp_socket = context.socket(zmq.REP)
        self.RDS_req_socket = context.socket(zmq.REQ)
        self.gui_sub_socket = context.socket(zmq.REP)
        self.RDS_pub_socket = context.socket(zmq.REQ)
        self.gui_resp_socket.bind(gui_resp_socket_url)
        self.RDS_req_socket.connect(RDS_req_socket_url)
        self.gui_sub_socket.bind(gui_sub_socket_url)
        self.RDS_pub_socket.connect(RDS_pub_socket_url)

    def run(self):
        while True:
            request = json.loads(self.gui_resp_socket.recv_json())

            if request["fcn"] == "connect":
                self.gui_resp_socket.send_json(self.connect())

            elif request["fcn"] == "set_area":
                self.gui_resp_socket.send_json(self.set_area())

            elif request["fcn"] == "request_POI":
                self.gui_resp_socket.send_json(self.request_poi(request["arg"]))

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

    def request_poi(self, poi):
        """Requests a point of interest to the RDS

        :param poi: Point of interest.
        :return The response message
        """
        #  TODO: Evolve this
        request = {"fcn": "add_poi"}
        request_args = {"client_id": 1, "force_que_id": 0}

        if poi["prio"]:
            request_args["force_que_id"] = random.randint()  # TODO: Guarantee that the number is unique

        request_args["coordinates"] = poi["coordinates"]
        request["arg"] = request_args
        self.RDS_pub_socket.send_json(json.dumps(request))
        resp = self.RDS_pub_socket.recv()
        return {"msg": "Poi added"}

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


