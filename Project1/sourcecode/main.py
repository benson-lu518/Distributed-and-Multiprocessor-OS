import argparse
import json
import multiprocessing
from time import sleep
from concurrent import futures
from termcolor import colored

import grpc

import branch_pb2_grpc
from Branch import Branch
from Customer import Customer


# Start branch gRPC server process
def serveBranch(branch):
    branch.createStubs()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    branch_pb2_grpc.add_BranchServicer_to_server(branch, server)
    port = str(50000 + branch.id)
    server.add_insecure_port("[::]:" + port)
    server.start()
    server.wait_for_termination()


# Start customer gRPC client processes
def serveCustomer(customer):
    customer.createStub()
    customer.executeEvents()

    return customer.output()
 

# Parse JSON & create objects/processes
def createProcesses(processes):
  
    # List of Branch objects
    branches = []
    # List of Branch IDs
    branchIds = []
    # List of Branch processes
    branchProcesses = []

    # Instantiate Branch objects
    try:
        for process in processes:
            if process["type"] == "branch":
                branch = Branch(process["id"], process["balance"], branchIds)
                branches.append(branch)
                branchIds.append(branch.id)
    except Exception as e:
        print(colored("Error creating Branch objects", e))
    
    try: 
        # Spawn Branch processes
        for branch in branches:
            branch_process = multiprocessing.Process(target=serveBranch, args=(branch,))
            branchProcesses.append(branch_process)
            branch_process.start()
    except Exception as e:
        print(colored("Error spawning Branch processes", e))

    # Wait for Branch server to start
    sleep(1.25)

    output_file = open("output.txt", "a")
    
    for process in processes:
        if process["type"] == "customer":
            customer=Customer(process["id"], process["events"])
            output=serveCustomer(customer)
            output_file.write(str(output) + "\n")
    
    output_file.close()

    # Terminate Branch processes
    for branchProcess in branchProcesses:
        branchProcess.terminate()


if __name__ == "__main__":
    # Setup command line argument for 'input_file'
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    args = parser.parse_args()

    try:
        # Load JSON file from 'input_file' arg
        input = json.load(open(args.input_file))

        # Initialize output file
        open("output.txt", "w").close()

        # Pass input file
        createProcesses(input)
    except FileNotFoundError:
        print(colored("Could not find input file '" + args.input_file + "'", "red"))
    except json.decoder.JSONDecodeError:
        print(colored("Error decoding JSON file", "red"))