"""Starts the threads and therefore the IMM application"""
from IMM.IMM_thread_init import *

fe_sub_thread = GuiSubThread()
rds_sub_thread = RDSSubThread()
req_resp_thread = ReqRespThread()
fe_sub_thread.start()
rds_sub_thread.start()
req_resp_thread.start()









