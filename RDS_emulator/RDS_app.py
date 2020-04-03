from RDS_emulator.RDS_emu import *


RDSPub_socket_url = "tcp://*:5571"
RDSSub_socket_url = "tcp://*:5570"
RDSRep_socker_url = "tcp://*:5572"

RDSPub_thread = IMMPubThread(RDSPub_socket_url)
RDSSub_thread = IMMSubThread(RDSSub_socket_url)
RDSRep_thread = IMMRepThread(RDSRep_socker_url)
RDSPub_thread.start()
RDSSub_thread.start()
RDSRep_thread.start()
