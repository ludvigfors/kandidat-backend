"""Initiates the socket urls"""
import zmq
context = zmq.Context()

RDS_pub_socket_url = "tcp://localhost:5570"
RDS_sub_socket_url = "tcp://localhost:5571"
RDS_req_socket_url = "tcp://localhost:5572"

gui_pub_socket_url = "tcp://*:4570"
gui_sub_socket_url = "tcp://*:4571"



