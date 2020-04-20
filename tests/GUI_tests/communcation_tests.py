import unittest
from IMM_database.database import use_test_database
import zmq
#Run the threads
from IMM.IMM_app import *

context = zmq.Context()

GUISubSocket = "tcp://localhost:4571"
GUI_to_BACKEND = context.socket(zmq.REQ) #start by sending messages
GUI_to_BACKEND.connect(GUISubSocket)

REQ_REP_BACKEND_RDS = "tcp://*:5572" #RDS will bind to this socket.
RDS_REQ_REP = context.socket(zmq.REP) #start by sending messages
RDS_REQ_REP.bind(REQ_REP_BACKEND_RDS)

class TestCommunication(unittest.TestCase):
    def setUp(self):
        use_test_database()

    """
    Test system communication TOP-DOWN.
    Send request to Back-End which sends a request to a RDS:
    - Simulates GUI request to Back-end checks the response from back-end.
    - Checks that the request to RDS from back-end are of correct form by
      listening to the RDS ports.
    """
    def test_connect(self):

        request_from_GUI = {"fcn":"connect"}
        GUI_to_BACKEND.send_json(json.dumps(request_from_GUI))
        resp_from_backend = GUI_to_BACKEND.recv_json()
        self.assertDictEqual(resp_from_backend, {"fcn":"ack", "name":"connect"})

    def test_disconnect(self):
        request_from_GUI = {"fcn":"disconnect"}
        GUI_to_BACKEND.send_json(json.dumps(request_from_GUI))
        resp_from_backend = GUI_to_BACKEND.recv_json()
        self.assertDictEqual(resp_from_backend, {'fcn': 'ack', 'name': 'disconnect'})

        message_to_RDS = RDS_REQ_REP.recv_json()
        self.assertDictEqual(message_to_RDS, {'fcn': 'quit', 'arg': ''})


if __name__ == '__main__':
    unittest.main()
