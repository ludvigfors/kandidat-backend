from IMM.IMM_thread_config import context, zmq, RDS_sub_socket_url, giu_pub_socket_url
from threading import Thread
import json


class RDSSubThread(Thread):
    """This thread subscribes to the RDS and handles the data (mostly images) received from the RDS"""
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
