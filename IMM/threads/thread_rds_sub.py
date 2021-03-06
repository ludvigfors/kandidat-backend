import numpy, time
from PIL import Image as PIL_image
from IMM.IMM_thread_config import context, zmq, RDS_sub_socket_url
from threading import Thread

from helper_functions import check_request
from IMM_database.database import Image, PrioImage, session_scope, UserSession, Coordinate
from helper_functions import get_path_from_root
import json, datetime


def generate_image_name(timestamp):
    with session_scope() as session:
        count = session.query(Image).filter_by(time_taken=timestamp).count()
    readable_time = datetime.datetime.fromtimestamp(timestamp)
    image_datetime = readable_time.strftime("%Y-%m-%d_%H-%M-%S")
    image_name = image_datetime + "_(" + str(count) + ")" + ".jpg"
    return image_name


def save_image(new_pic):
    # TODO: Organize how the images are saved
    jpg_image = PIL_image.fromarray(new_pic)
    timestamp = int(time.time())
    image_name = generate_image_name(timestamp)
    image_path = get_path_from_root("/IMM/images/") + image_name
    jpg_image.save(image_path)
    return timestamp, image_name


def get_session_id():
    pass


def get_dummy_session_id():
    session_id = 1
    with session_scope() as session:
        if session.query(UserSession).count() == 0:
            dummy_session = UserSession(start_time=100, drone_mode="AUTO")
            session.add(dummy_session)

    with session_scope() as session:
        session_id = session.query(UserSession).first().id

    return session_id


def save_to_database(img_arg, new_pic, file_data):

    def coordinate_from_json(json):
        return Coordinate(lat=json["lat"], long=json["long"])

    session_id = get_dummy_session_id()

    # Gather image info
    width = len(new_pic[0])
    height = len(new_pic)
    img_type = img_arg["type"]
    up_left = coordinate_from_json(img_arg["coordinates"]["up_left"])
    up_right = coordinate_from_json(img_arg["coordinates"]["up_right"])
    down_right = coordinate_from_json(img_arg["coordinates"]["down_right"])
    down_left = coordinate_from_json(img_arg["coordinates"]["down_left"])
    center = coordinate_from_json(img_arg["coordinates"]["center"])

    image = Image(
        session_id=session_id,
        time_taken=file_data[0],
        width=width,
        height=height,
        type=img_type,
        file_name=file_data[1],
        up_left=up_left,
        up_right=up_right,
        down_right=down_right,
        down_left=down_left,
        center=center
    )

    with session_scope() as session:
        session.add(image)


def match_image_to_tile(img_file_name):
    # This function might be heavy work so maybe it should run in a worker thread.

    with session_scope() as session:
        image = session.query(Image).filter_by(file_name=img_file_name).first()

    i=0



class RDSSubThread(Thread):
    """This thread subscribes to the RDS and handles the data (mostly images) received from the RDS"""
    def __init__(self, thread_handler):
        super().__init__()
        self.RDS_sub_socket = context.socket(zmq.REP)
        self.RDS_sub_socket.connect(RDS_sub_socket_url)
        self.thread_handler = thread_handler
        self.running = True

    def recv_image_array(self, metadata, flags=0, copy=True, track=False):
        """Receives and returns the image converted to a numpy array"""
        msg = self.RDS_sub_socket.recv(flags=flags, copy=copy, track=track)
        self.RDS_sub_socket.send_json(json.dumps({"msg": "ack"}))
        buf = memoryview(msg)
        image_array = numpy.frombuffer(buf, dtype=metadata["dtype"])
        return image_array.reshape(metadata["shape"])

    def run(self):
        while self.running:
            try:
                request = self.RDS_sub_socket.recv_json()
                check_request(request)
                if "image_md" in request:
                    # We have a new image
                    new_pic = self.recv_image_array(request["image_md"])
                    img_file_data = save_image(new_pic)
                    save_to_database(request["arg"], new_pic, img_file_data)
                    tile_image = match_image_to_tile(img_file_data[1])
                    self.send_tile_to_gui(tile_image)

            except:
                raise

    def send_tile_to_gui(self, tile_image):
        """Send tile image to gui"""

        # Not sure how we should pass the image tile yet, code below is work in progress
        msg = {"fcn": "new_pic", "arg": {"image_id": 1}}  # This notify message will change later
        request = {"IMM_fcn": "send_to_gui", "arg": msg}

        # contact gui pub thread
        self.thread_handler.get_gui_pub_thread().add_request(request)

    def stop(self):
        self.RDS_sub_socket.close()
        context.destroy()
        self.running = False

