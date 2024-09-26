# CSE 531 Distributed and Multiprocessor Operating Systems

# Distributed Banking System Using gRPC

## Overview
This repository contains three projects implementing a distributed banking system using gRPC. The system allows customers to perform banking operations such as withdrawing, depositing, and querying balances across multiple branches of the bank.

### Projects
1. **CSE-531_Project-1** - Basic Banking Operations
2. **CSE-531_Project-2** - Logic Clock Implementation
3. **CSE-531_Project-3** - Client-Centric Banking Operations

## Technologies Used
- **Development Environment:**
  - Python: 3.8.8
  - IDE: VSCode
  - Anaconda: 2021.05

- **Python Packages:**
  - Multiprocessing
  - Concurrent
  - gRPC: 1.32.0

## Project Details

### CSE-531_Project-1 --- gRPC Project

#### Project Statement
Implement a basic distributed banking system where customers can communicate with specific branches to perform banking operations.

#### Project Goal
- Process a JSON file containing multiple customer events and account balances.
- Generate a corresponding output text file.

#### Implementation Steps
1. Define serialized structured data in a `.proto` file.
2. Generate Python source files from the `.proto` file.
3. Create `Branch.py` as the server side to handle requests.
4. Create `Customer.py` as the client side to execute events.
5. Control the program with `Main.py`.

### CSE-531_Project-2 --- Logic Clock Project

#### Project Statement
Extend the initial project to ensure that all events are ordered using a logical clock.

#### Project Goal
- Process a JSON file containing events and IDs while maintaining event order.
- Generate a corresponding output text file with logic clock numbers.

#### Implementation Steps
1. Update local clock handling in `Customer.py`.
2. Implement functions in `Branch.py` for event receiving and propagation.
3. Separate branch and customer into two services in `main.py`.
4. Write output results to a JSON file.

### CSE-531_Project-3 --- Client-Centric Project

#### Project Statement
Enhance the banking system to allow customers to interact with different branches for transactions.

#### Project Goal
- Extend the implementation of `Branch.Withdraw` and `Branch.Deposit` to enforce Monotonic Writes and Read Your Writes policies.

#### Implementation Steps
1. Define serialized structured data in a `.proto` file.
2. Generate Python source files from the `.proto` file.
3. Create `Branch.py` to handle branch-specific operations.
4. Create `Customer.py` to handle customer requests.
5. Control the program with `Main.py`.

## Results
- The output from each project will generate files (text or JSON) corresponding to the input files, detailing the results of banking operations.

### Example Outputs
- For **Project 1**, you might see:
  ```json
  {'id': 1, 'recv': [{'interface': 'deposit', 'result': 'success'}, {'interface': 'query', 'balance': 410}]}
