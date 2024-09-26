from time import sleep

import grpc
from termcolor import colored

import branch_pb2_grpc
from branch_pb2 import MsgRequest


class Customer:
    def __init__(self, id, events,type):
        self.id = id
        self.events = events
        self.recvCustmerMsg = list()
        # self.recvBranchMsg = list()
        self.stub = None
        self.clock = 1

    # Setup gRPC channel & client stub for branch 
    # Stub is for address 
    def createStub(self):
        port = str(50000 + self.id)
        channel = grpc.insecure_channel("localhost:" + port)
        self.stub = branch_pb2_grpc.BranchStub(channel)

    # Send gRPC request for each event
    def executeEvents(self,type):
        if type == "customer":
            clock=1
            for event in self.events:
                # Sleep 3 seconds for 'query' events
                if event["interface"] == "query":
                    sleep(3)

                    # Send request to Branch server and get response
                    response = self.stub.MsgDelivery(
                        MsgRequest(id=event["customer-request-id"], interface=event["interface"], money=event["money"],type="customer")
                    )
                    # Create msg to be appended to self.recvMsg list
                    msg = {"customer-request-id": response.id,"logical_clock": clock ,"interface": response.interface,"comment": "event_send from customer "+ str(self.id),"balance": response.money }
                else:
                    # Send request to Branch server and get response
                    response = self.stub.MsgDelivery(
                        MsgRequest(id=event["customer-request-id"], interface=event["interface"],type="customer")
                    )
                    # Create msg to be appended to self.recvMsg list
                    msg = {"customer-request-id": response.id,"logical_clock": clock,"interface": response.interface,"comment": "event_send from customer "+ str(self.id) }
                clock+=1
            

                self.recvCustmerMsg.append(msg)
        elif type == "branch":
            clock=1
            for event in self.events:
                # Sleep 3 seconds for 'query' events
                if event["interface"] == "query":
                    sleep(3)

                    # Send request to Branch server and get response
                    response = self.stub.MsgDelivery(
                        MsgRequest(id=event["customer-request-id"], interface=event["interface"], money=event["money"],type="branch",clock=clock)
                    )
                    # Update local clock
                    clock = max(clock, response.clock) + 1
                    # Create msg to be appended to self.recvMsg list
                    # msg = {"customer-request-id": response.id,"logical_clock": clock ,"interface": response.interface,"comment": "event_send from customer "+ str(self.id),"balance": response.money }
                else:
                    # Send request to Branch server and get response
                    response = self.stub.MsgDelivery(
                        MsgRequest(id=event["customer-request-id"], interface=event["interface"],type="branch",clock=self.clock)
                    )
                    # Update local clock
                    clock = max(clock, response.clock) + 1
                    # Create msg to be appended to self.recvMsg list
                    # msg = {"result": response.result}
                clock+=1
            

                # self.recvBranchMsg.append(msg)
    # Generate output msg
    def output(self,type):
        if type == "customer":
            return {"id": self.id, "type":"customer","events": self.recvCustmerMsg}
        elif type == "branch":
            pass