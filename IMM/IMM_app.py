"""Starts the threads and therefore the IMM application"""
from IMM.thread_handler import ThreadHandler
from flask import Flask, jsonify, request
import json
from flask_socketio import SocketIO, join_room, emit

app = Flask(__name__)
thread_handler = ThreadHandler()
socketio = SocketIO(app)



@socketio.on("connect")
def on_connect():
    # Unclear what this should do? Issue: #43
    socketio.emit("response", "CONNECTED TO BACKEND")
    return {"fcn":"unit_test_ack", "name":"connect"}


@socketio.on("check_alive")
def on_check_alive():
    # TODO: Implement this
    # Sends request to rds pub thread
    pass

@socketio.on("quit")
def on_quit():
    # TODO: Implement this
    # Sends request to rds pub thread
    pass

@socketio.on("set_area")
def on_set_area():
    # TODO: Implement this
    # Sends request to rds pub thread
    pass

@socketio.on("request_view")
def on_request_view(data):
    # TODO: Implement this
    print("recieved request for a POI")
    print(data)
    emit("response", data)
    # Sends request to rds pub thread
    pass


@socketio.on("request_priority_view")
def on_request_priority_view():
    # TODO: Implement this
    # Sends request to rds pub thread
    pass


@socketio.on("clear_queue")
def on_clear_queue():
    # TODO: Implement this
    # Sends request to rds pub thread
    pass


@socketio.on("set_mode")
def on_set_mode():
    # TODO: Implement this
    # Sends request to rds pub thread
    pass

@socketio.on("get_image_by_id")
def on_get_image_by_id(self):
    # TODO: Implement this
    pass

@socketio.on("get_info")
def on_get_info(self):
    # TODO: Implement this
    pass

@socketio.on("/request_image",)
def request_image():
    """Requests a point of interest"""
    # Sends request to rds pub thread
    #poi = json.loads(request.data)
    # Psudocode
    # if poi in IMM_database:
    # return db.image.metadata
    # else
    #thread_handler.get_rds_pub_thread().add_request(poi)
    return

@socketio.on("ack")
def on_ack():
    # Implement
    pass

if __name__=="__main__":
    thread_handler.start_threads()
    socketio.run(app, port=8080)
