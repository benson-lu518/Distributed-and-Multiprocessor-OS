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

def serveBranchForBranch(branch):
    branch.createStubs()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    branch_pb2_grpc.add_BranchServicer_to_server(branch, server)
    port = str(50000 + branch.id)
    server.add_insecure_port("[::]:" + port)
    server.start()

    # Stagger writing to the output file to maintain order of pid's
    sleep(0.5 * branch.id)
    output_array = json.load(open("output.json"))
    output_array.append({"id": branch.id, "type": "branch","events": branch.output()})
    output = json.dumps(output_array, indent=4)
    output_file = open("output.json", "w")
    output_file.write(output)
    output_file.close()

    server.wait_for_termination()



# Start customer gRPC client processes
def serveCustomer(customer,type):
    customer.createStub()

    if type == "customer":  

        customer.executeEvents(type)

        return customer.output(type)
    elif type == "branch":
 
        customer.executeEvents(type)

        return customer.output(type)

# Parse JSON & create objects/processes
def createProcesses(processes):
    # List of Customer objects
    customers = []
    # List of Customer processes
    customerProcesses = []
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
            branch_process = multiprocessing.Process(target=serveBranchForBranch, args=(branch,))
            branchProcesses.append(branch_process)
            branch_process.start()
    except Exception as e:
        print(colored("Error spawning Branch processes", e))

    # Wait for Branch server to start
    sleep(1.25)

    output_array = json.load(open("output.json"))
    
    for process in processes:
        if process["type"] == "customer":
            customer=Customer(process["id"], process["customer-requests"],process["type"])
            output=serveCustomer(customer,"customer")
            output_array.append(output)
            output = json.dumps(output_array, indent=4)
            output_file = open("output.json", "w")
            output_file.write(output)
        
    
    output_file.close()

    # Terminate Branch processes
    for branchProcess in branchProcesses:
        branchProcess.terminate()
    
    sleep(1.25)

    # for branch ------------------------
    for branch in branches:
        branch_process = multiprocessing.Process(target=serveBranchForBranch, args=(branch,))
        branchProcesses.append(branch_process)
        branch_process.start()

    # Allow branch processes to start
    sleep(1.25)

    # Instantiate Customer objects
    for process in processes:
        if process["type"] == "customer":
            customer = Customer(process["id"], process["customer-requests"],"branch")
            customers.append(customer)

    # Spawn Customer processes
    for customer in customers:
        customer_process = multiprocessing.Process(target=serveCustomer, args=(customer,"branch"))
        customerProcesses.append(customer_process)
        customer_process.start()

    # Wait for Customer processes to complete
    for customerProcess in customerProcesses:
        customerProcess.join()

    # Allow branches to complete output before terminating
    sleep(1)

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
        output_file = open("output.json", "w")
        output_file.write("[]")
        output_file.close()
        # Pass input file
        createProcesses(input)
    except FileNotFoundError:
        print(colored("Could not find input file '" + args.input_file + "'", "red"))
    except json.decoder.JSONDecodeError:
        print(colored("Error decoding JSON file", "red"))