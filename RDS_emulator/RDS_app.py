from RDS_emulator.RDS_emu import *


RDSPub_socket_url = "tcp://*:5571"
RDSSub_socket_url = "tcp://*:5570"
RDSRep_socker_url = "tcp://*:5572"


class RDSThreadHandler:
    def __init__(self):
        self.drone_thread = DroneThread()
        self.drone_thread.start()
        self.RDSPub_thread = IMMPubThread(RDSPub_socket_url, self.drone_thread)
        self.RDSSub_thread = IMMSubThread(RDSSub_socket_url, self.drone_thread)
        self.RDSRep_thread = IMMRepThread(RDSRep_socker_url, self.drone_thread)

    def start_threads(self):
        self.RDSSub_thread.start()
        self.RDSPub_thread.start()
        self.RDSRep_thread.start()

    def stop_threads(self):
        self.drone_thread.stop()
        self.RDSSub_thread.stop()
        self.RDSPub_thread.stop()
        self.RDSRep_thread.stop()


