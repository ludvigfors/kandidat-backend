from IMM.IMM_thread_config import context, zmq, gui_resp_socket_url, RDS_req_socket_url
from threading import Thread
import json


class ReqRespThread(Thread):
    """This thread handles the requests sent by the gui.
        It will contact the RDS for the requested information"""

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
