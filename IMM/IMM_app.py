"""Starts the threads and therefore the IMM application"""
from IMM.threads.thread_rds_pub import *
from IMM.threads.thread_gui_pub import *
rds_pub_thread = RDSPubThread()
gui_pub_thread = GUIPubThread()

from IMM.threads.thread_gui_sub import *
from IMM.threads.thread_rds_sub import *


"""
General info about zeroMQ
zmq.REQ: Start by sending messages
zmq.REP: Start by receiving messages
"""

rds_sub_thread = RDSSubThread()
gui_sub_thread = GuiSubThread()
rds_pub_thread.start()
rds_sub_thread.start()
gui_pub_thread.start()
gui_sub_thread.start()









