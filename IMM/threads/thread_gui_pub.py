from IMM.IMM_thread_config import context, zmq, gui_pub_socket_url
from threading import Thread
from helper_functions import check_request
import json


class GUIPubThread(Thread):
    """This thread sends data to the GUI"""

    def __init__(self):
        super().__init__()
        self.gui_pub_socket = context.socket(zmq.REQ)
        self.gui_pub_socket.bind(gui_pub_socket_url)
        self.request_queue = []

    def run(self):
        while True:
            if len(self.request_queue) > 0:
                request = self.request_queue.pop(0)
                check_request(request)
                if request["IMM_fcn"] == "send_to_gui":
                    self.send_to_gui(request["arg"])

    def send_to_gui(self, param):
        self.gui_pub_socket.send_json(json.dumps(param))
        resp = self.gui_pub_socket.recv_json()

    def add_request(self, request):
        self.request_queue.append(request)
