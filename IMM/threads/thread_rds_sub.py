from IMM.IMM_thread_config import context, zmq, RDS_sub_socket_url
from threading import Thread
from IMM.helper_functions import check_request
from IMM.IMM_app import gui_pub_thread
import json


class RDSSubThread(Thread):
    """This thread subscribes to the RDS and handles the data (mostly images) received from the RDS"""
    def __init__(self):
        super().__init__()
        self.RDS_sub_socket = context.socket(zmq.REP)
        self.RDS_sub_socket.connect(RDS_sub_socket_url)


    def run(self):
        while True:
            new_pic = self.RDS_sub_socket.recv_json()

            check_request(new_pic)

            self.RDS_sub_socket.send_json(json.dumps({"msg": "ack"}))
            self.save_to_database(new_pic)
            self.new_pic_notify_gui()

    def save_to_database(self, new_pic):
        # TODO: Save new pic to database here
        pass

    def new_pic_notify_gui(self):
        """Run thread_gui_pub"""

        msg = {"fcn": "new_pic", "arg":{"image_id": 1}}  # This notify message will change later
        request = {"IMM_fcn": "send_to_gui", "arg": msg}

        # contact gui pub thread
        gui_pub_thread.add_request(request)
