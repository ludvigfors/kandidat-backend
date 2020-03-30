"""Starts the threads and therefore the IMM application"""
from IMM.threads.thread_req_resp_gui import *
from IMM.threads.thread_sub_rds_ import *

"""
General info about zeroMQ
zmq.REQ: Start by sending messages
zmq.REP: Start by receiving messages
"""

rds_sub_thread = RDSSubThread()
req_resp_thread = GuiReqRespThread()
rds_sub_thread.start()
req_resp_thread.start()









