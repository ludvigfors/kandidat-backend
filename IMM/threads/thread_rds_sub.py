import numpy

from IMM.IMM_thread_config import context, zmq, RDS_sub_socket_url
from threading import Thread
from IMM.helper_functions import check_request
from IMM.IMM_app import gui_pub_thread
from database.database import Image, PrioImage, get_database
import json


class RDSSubThread(Thread):
    """This thread subscribes to the RDS and handles the data (mostly images) received from the RDS"""
    def __init__(self):
        super().__init__()
        self.RDS_sub_socket = context.socket(zmq.REP)
        self.RDS_sub_socket.connect(RDS_sub_socket_url)

    def recv_image_array(self, metadata, flags=0, copy=True, track=False):
        msg = self.RDS_sub_socket.recv(flags=flags, copy=copy, track=track)
        buf = memoryview(msg)
        A = numpy.frombuffer(buf, dtype=metadata["dtype"])
        return A.reshape(metadata["shape"])

    def run(self):
        while True:
            request = self.RDS_sub_socket.recv_json(flags=0)
            # If zmq.sndmore
            check_request(request)
            if "image_md" in request:
                # We have a new image
                new_pic = self.recv_image_array(request["image_md"])
                self.save_to_database(request["arg"], new_pic)
                self.new_pic_notify_gui()

            self.RDS_sub_socket.send_json(json.dumps({"msg": "ack"}))

    def save_to_database(self, img_arg, new_pic):
        # TODO: Save new pic to database here
        i = 0
        # session_id = get_session_id()
        # time_taken = get_time_taken() ??
        session_id = 0
        time_taken = 100

        # Gather image info
        width = len(new_pic[0])
        height = len(new_pic)
        type = img_arg["type"]
        up_left_x = img_arg["coordinates"]["up_left"]["long"]
        up_left_y = img_arg["coordinates"]["up_left"]["lat"]
        up_right_x = img_arg["coordinates"]["up_right"]["long"]
        up_right_y = img_arg["coordinates"]["up_right"]["lat"]
        down_right_x = img_arg["coordinates"]["down_right"]["long"]
        down_right_y = img_arg["coordinates"]["down_right"]["lat"]
        down_left_x = img_arg["coordinates"]["down_left"]["long"]
        down_left_y = img_arg["coordinates"]["down_left"]["lat"]
        # TODO: Add center positions

        image = Image(session_id, time_taken, width, height, type,
                      __up_left_x=up_left_x,
                      __up_left_y=up_left_y,
                      __up_right_x=up_right_x,
                      __up_right_y=up_right_y,
                      __down_left_x=down_left_x,
                      __down_left_y=down_left_y,
                      __down_right_x=down_right_x,
                      __down_right_y=down_right_y)




    def new_pic_notify_gui(self):
        """Run thread_gui_pub"""

        msg = {"fcn": "new_pic", "arg":{"image_id": 1}}  # This notify message will change later
        request = {"IMM_fcn": "send_to_gui", "arg": msg}

        # contact gui pub thread
        gui_pub_thread.add_request(request)
