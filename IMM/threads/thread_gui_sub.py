from IMM.IMM_thread_config import context, zmq, gui_sub_socket_url
from IMM.helper_functions import check_request
from threading import Thread
from IMM.IMM_app import rds_pub_thread
import json


class GuiSubThread(Thread):
    """This thread handles the requests sent by the gui"""

    def __init__(self):
        super().__init__()
        self.gui_sub_socket = context.socket(zmq.REP)
        self.gui_sub_socket.bind(gui_sub_socket_url)

    def run(self):
        while True:
            request = json.loads(self.gui_sub_socket.recv_json())

            check_request(request)

            if request["fcn"] == "connect":
                self.gui_sub_socket.send_json(self.connect())
                self.connect()
            elif request["fcn"] == "set_area":
                self.gui_sub_socket.send_json(self.set_area())

            elif request["fcn"] == "request_POI":
                self.gui_sub_socket.send_json(self.request_poi(request))

            elif request["fcn"] == "request_image_by_id":
                self.gui_sub_socket.send_json(self.get_image_by_id(request))

            elif request["fcn"] == "get_info":
                self.gui_sub_socket.send_json(self.get_info())

            elif request["fcn"] == "set_mode":
                self.gui_sub_socket.send_json(self.set_mode())

            elif request["fcn"] == "clear_que":
                self.gui_sub_socket.send_json(self.clear_queue())

            elif request["fcn"] == "que_ETA":
                self.gui_sub_socket.send_json(self.queue_eta())

            elif request["fcn"] == "quit":
                self.gui_sub_socket.send_json(self.disconnect())

            else:
                self.gui_sub_socket.send_json(json.dumps({"msg": "nothing happened"}))

    def connect(self):
        # TODO: Implement this
        pass

    def set_area(self):
        # TODO: Implement this
        # Sends request to rds pub thread
        pass

    def get_info(self):
        # TODO: Implement this
        pass

    def request_poi(self, poi):
        """Requests a point of interest"""
        # Sends request to rds pub thread

        # Psudocode
        # if poi in database:
        # return db.image.metadata
        # else
        rds_pub_thread.add_request(poi)
        return {"msg":"poi added"}

    def disconnect(self):
        # TODO: Implement this
        pass

    def set_mode(self):
        # TODO: Implement this
        # Sends request to rds pub thread
        pass

    def clear_queue(self):
        # TODO: Implement this
        # Sends request to rds pub thread
        pass

    def queue_eta(self):
        # TODO: Implement this
        pass

    def get_image_by_id(self, request):
        """Get the image from the database with the specified ID"""
        pass




