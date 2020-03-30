"""Starts the threads and therefore the IMM application"""
from IMM.threads.thread_req_resp import *
from IMM.threads.thread_sub_gui import *
from IMM.threads.thread_sub_rds_ import *

"""
General info about zeroMQ
zmq.REQ: Start by sending messages
zmq.REP: Start by receiving messages
"""

fe_sub_thread = GuiSubThread()
rds_sub_thread = RDSSubThread()
req_resp_thread = ReqRespThread()
fe_sub_thread.start()
rds_sub_thread.start()
req_resp_thread.start()









