
from IMM.threads.thread_rds_pub import RDSPubThread
from IMM.threads.thread_rds_sub import RDSSubThread
from IMM.threads.thread_gui_pub import GUIPubThread


class ThreadHandler():
    """Regularly fetches information from the RDS and processes client requests"""

    def __init__(self):
        super().__init__()
        self.rds_pub_thread = RDSPubThread(self)
        self.gui_pub_thread = GUIPubThread(self)
        self.rds_sub_thread = RDSSubThread(self)

    def start_threads(self):
        self.rds_pub_thread.start()
        self.rds_sub_thread.start()
        self.gui_pub_thread.start()

    def stop_threads(self):
        self.rds_pub_thread.stop()
        self.rds_sub_thread.stop()
        self.gui_pub_thread.stop()

    def get_rds_pub_thread(self):
        return self.rds_pub_thread

    def get_rds_sub_thread(self):
        return self.rds_sub_thread

    def get_gui_pub_thread(self):
        return self.gui_pub_thread

