from time import sleep

import grpc
from termcolor import colored

import branch_pb2_grpc
from branch_pb2 import MsgRequest


class Customer:
    def __init__(self, id, events):
        self.id = id
        self.events = events
        self.recvMsg = list()
        self.stub = None

    # Setup gRPC channel & client stub for branch 
    # Stub is for address 
    def createStub(self):
        port = str(50000 + self.id)
        channel = grpc.insecure_channel("localhost:" + port)
        self.stub = branch_pb2_grpc.BranchStub(channel)

    # Send gRPC request for each event
    def executeEvents(self):
        for event in self.events:
            # Sleep 3 seconds for 'query' events
            if event["interface"] == "query":
                sleep(3)

                # Send request to Branch server and get response
                response = self.stub.MsgDelivery(
                    MsgRequest(id=event["id"], interface=event["interface"])
                )
                # Create msg to be appended to self.recvMsg list
                msg = {"interface": response.interface}
            else:
                # Send request to Branch server and get response
                response = self.stub.MsgDelivery(
                    MsgRequest(id=event["id"], interface=event["interface"], money=event["money"])
                )
                # Create msg to be appended to self.recvMsg list
                msg = {"interface": response.interface, "result": response.result}

            # Add 'balance' entry for 'query' events
            if response.interface == "query":
                msg["balance"] = response.money

            self.recvMsg.append(msg)

    # Generate output msg
    def output(self):
        return {"id": self.id, "recv": self.recvMsg}

