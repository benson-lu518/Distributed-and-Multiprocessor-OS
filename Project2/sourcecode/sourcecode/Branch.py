from concurrent import futures
from time import sleep

import branch_pb2_grpc
import grpc
import numpy as np
from branch_pb2 import MsgRequest, MsgResponse
from termcolor import colored


class Branch(branch_pb2_grpc.BranchServicer):
    def __init__(self, id, balance, branches):
        self.id = id
        self.balance = balance
        self.branches = branches
        self.stubList = list()
        self.recvMsg = list()
        self.events = list()
        self.clock = 1

    # Setup gRPC channel & client stub for each branch
    def createStubs(self):
        for branchId in self.branches:
            if branchId != self.id:
                port = str(50000 + branchId)
                channel = grpc.insecure_channel("localhost:" + port)
                self.stubList.append(branch_pb2_grpc.BranchStub(channel))
    # MsgDelivery, MsgPropagation -> two services in branch.proto
    # Incoming MsgRequest from Customer transaction
    def MsgDelivery(self, request, context):
        if request.type == "customer":
            return self.ProcessMsg(request, False)
        elif request.type == "branch":
            if request.interface != "query":
                print(request)
                self.Event_Receive(request)
                self.Event_Propagate(request)        
        
            return self.ProcessMsg(request, False)

    # Incoming MsgRequest from Branch propagation
    def MsgPropagation(self, request, context):
        return self.ProcessMsg(request, False)

    # Customer -> MsgDelivery -> ProcessMsg -> MsgResponse -> Customer
    # Handle received Msg, generate and return a MsgResponse
    def ProcessMsg(self, request, propagate):
        # if request.interface != "query":
        #     if not propagate:
        #         pass
        #     else:
        #         self.Event_Propagate(request)
        result = "success"
        if request.money < 0:
            result = "fail"
        elif request.interface == "query":
            pass
        elif request.interface == "deposit":
            self.balance += request.money
            if propagate == True:
                self.Propagate_Deposit(request)
        elif request.interface == "withdraw":
            if self.balance >= request.money:
                self.balance -= request.money
                if propagate == True:
                    self.Propagate_Withdraw(request)
            else:
                result = "fail"
        else:
            result = "fail"

        # Create msg to be appended to self.recvMsg list
        msg = {"interface": request.interface, "result": result,"id":self.id}

        # Add 'money' entry for 'query' events
        if request.interface == "query":
            msg["money"] = request.money

        self.recvMsg.append(msg)

        return MsgResponse(interface=request.interface, result=result, money=self.balance,id=request.id)

    # Propagate Customer withdraw to other Branches
    def Propagate_Withdraw(self, request):
        for stub in self.stubList:
            stub.MsgPropagation(MsgRequest(id=request.id, interface="withdraw", money=request.money))

    # Propagate Customer deposit to other Branches
    def Propagate_Deposit(self, request):
        for stub in self.stubList:
            stub.MsgPropagation(MsgRequest(id=request.id, interface="deposit", money=request.money))


    # Receive event from Customer (max+1)
    def Event_Receive(self, request):
        self.clock = max(self.clock, request.clock) + 1
        self.events.append({"customer-request-id": request.id, "logical_clock": self.clock ,"interface": request.interface , "comment": "event_receive from customer "+ str(request.id)})
    # Receive propagated event from Branch (max + 1)
    def Event_Propagate(self, request):
        self.clock = max(self.clock, request.clock) + 1
        self.events.append({"customer-request-id": request.id, "logical_clock": self.clock ,"interface": request.interface , "comment": "event_sent to branch "+ str(request.id)})
     # Generate output msg
    def output(self):
        return self.events