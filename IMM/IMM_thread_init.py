"""Initiates the socket urls and starts imports all threads"""

import zmq
context = zmq.Context()

RDS_pub_socket_url = "tcp://localhost:5570"
RDS_sub_socket_url = "tcp://localhost:5571"
RDS_req_socket_url = "tcp://localhost:5572"

giu_pub_socket_url = "tcp://*:4570"
gui_sub_socket_url = "tcp://*:4571"
gui_resp_socket_url = "tcp://*:4572"

"""
zmq.REQ: Start by sending messages
zmq.REP: Start by receiving messages
"""

from IMM.threads.thread_req_resp import *
from IMM.threads.thread_sub_gui import *
from IMM.threads.thread_sub_rds_ import *