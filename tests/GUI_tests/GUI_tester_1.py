"""A mock simulating the GUI making requests"""
from RDS_emulator.RDS_app import *
from IMM.IMM_app import *
context = zmq.Context()

# Run this the first time the test goes to add the IMM_database (images.db)
#init_db_and_add_image()


sub_socket_url = "tcp://localhost:4570"
req_socket_url = "tcp://localhost:4571"


class PubThread(Thread):

    def __init__(self):
        super().__init__()
        self.req_socket = context.socket(zmq.REQ)
        self.req_socket.connect(req_socket_url)

    def run(self):
        # Simulating frontend making a series of calls

        # Connect to backend
        req1 = {}

        # Set area
        req2 = {}

        # Request point of interest
        req3 = {
            "fcn": "request_POI",
            "arg":
                {
                   # "client_id": 1, # Not implemented yet
                    "prio" : False,
                    "coordinates" : {
                "up_left":
                    {
                        "lat":59,
                        "long":16
             },
                 "up_right":
                     {
                         "lat":58,
                         "long":16
                     },
                 "down_left":
                     {
                         "lat":58,
                         "long":16
                     },
                 "down_right":
                     {"lat":58,
                      "long":16
                      },
                 "center":
                     {
                         "lat":58,
                         "long":16
                     }
             }

            }
        }

        print("Sending add poi")
        self.req_socket.send_json(json.dumps(req3))
        resp = self.req_socket.recv()
        # print(resp)


class SubThread(Thread):
    def __init__(self):
        super().__init__()
        self.sub_socket = context.socket(zmq.REP)
        self.sub_socket.connect(sub_socket_url)

    def run(self):
        while True:
            message = json.loads(self.sub_socket.recv_json())
            self.sub_socket.send_json(json.dumps({"msg":"ack"}))
            if message["fcn"] == "new_pic" and "image_id" in message["arg"]:
                print("Test successful")
            else:
                print("Test failed")
            #if message == "notify":
                # Request image by id


ppthread = PubThread()
ppthread.start()
subscriber_thread = SubThread()
subscriber_thread.start()



