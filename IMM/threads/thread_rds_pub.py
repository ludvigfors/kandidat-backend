from IMM.IMM_thread_config import context, zmq, RDS_req_socket_url, RDS_pub_socket_url
from threading import Thread
from IMM.helper_functions import check_request
import json
import random


class RDSPubThread(Thread):
    """Regularly fetches information from the RDS and processes client requests"""

    def __init__(self):
        super().__init__()
        self.RDS_req_socket = context.socket(zmq.REQ)
        self.RDS_pub_socket = context.socket(zmq.REQ)
        self.RDS_req_socket.connect(RDS_req_socket_url)
        self.RDS_pub_socket.connect(RDS_pub_socket_url)
        self.request_queue = []

    def run(self):
        while True:
            if len(self.request_queue) > 0:
                request = self.request_queue.pop(0)

                check_request(request)

                if request["fcn"] == "set_area":
                    self.set_area()

                elif request["fcn"] == "request_POI":
                    self.request_poi(request["arg"])

                elif request["fcn"] == "set_mode":
                    self.set_mode()

            # do regular update stuff below (get_info() que_eta etc)

    def add_request(self, request):
        self.request_queue.append(request)

    def request_poi(self, poi):
        """Requests a point of interest from the RDS

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

    def set_area(self):
        pass

    def set_mode(self):
        pass


