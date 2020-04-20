from threading import Thread
from helper_functions import check_request
import json


class GUIPubThread(Thread):
    """This thread sends data to the GUI"""

    def __init__(self, thread_handler):
        super().__init__()
        self.request_queue = []
        self.running = True

    def run(self):
        while self.running:
            if len(self.request_queue) > 0:
                request = self.request_queue.pop(0)
                check_request(request)
                if request["IMM_fcn"] == "send_to_gui":
                    self.send_to_gui(request["arg"])

    def send_to_gui(self, param):
        #socketio.emit("response", data_to_send, room = correct_session_room)

        # old - self.gui_pub_socket.send_json(json.dumps(param))
        # old - resp = self.gui_pub_socket.recv_json()
        print("Notify gui")

    def add_request(self, request):
        self.request_queue.append(request)

    def stop(self):
        self.running = False
