#!/usr/bin/env python3
from blockchain import Blockchain
import argparse

def parse(command):
    parser = argparse.ArgumentParser(description='Blockchain Chain of Custody Management System')
    parser.add_argument('bchoc')
    parser.add_argument('action', choices=['add', 'checkout', 'show', 'remove', 'init', 'verify'], help='Action to perform on the blockchain')
    parser.add_argument('-i', '--item_id', help='Item ID for the blockchain operation')
    parser.add_argument ('-c', '--case_id', help= 'Case ID for the blockchain operation')
    parser.add_argument('-p', '--password', help='Password for blockchain verification')

    try: #if argparse encounters an invalid input it exits the system so if an invalid command is passed we have to 
        #raise an exception and handle accordingly so the program keeps prompting the user for input
        args = parser.parse_args(command.split())
        return args
    except SystemExit:
        # This handles invalid input so program doesnt exit
        print("Invalid command or arguments. Please try again.")
        return None

def main():
    blockchain = Blockchain() #creates instance of blockchain structure which automatically calls init function

    while True:
        command = input("Enter command: ")
        args = parse(command)

        if args is None : 
            continue 

        elif args.action == 'add':
            if args.item_id:
                data = {"action": "add", "case_id": args.case_id, "item_id": args.item_id}
                blockchain.add_block(data)
                outcome = blockchain.add_block(data)
                if (outcome == True):
                    print(f"Checked out item {args.item_id} from the blockchain.")
                else: 
                    print("Block add failed")
            else:
                print("Item ID is required for 'checkout' action.")

        elif args.action == 'checkout':
            if args.item_id:
                data = {"action": "checkout", "item_id": args.item_id}
                outcome = blockchain.add_block(data)
                if (outcome == True):
                    print(f"Checked out item {args.item_id} from the blockchain.")
                else: 
                    print("Block checkout failed")
            else:
                print("Item ID is required for 'checkout' action.")

        elif args.action == 'show':
            for block in blockchain._read_blocks():
                print(f"Block {block.index} - Hash: {block.hash}")
                print("Timestamp:", block.timestamp)
                print("Data:", block.data)
                print("Previous Hash:", block.previous_hash)
                print("\n")

        elif args.action == 'remove':
            if args.item_id:
                data = {"action": "remove", "item_id": args.item_id}
                blockchain.add_block(data)
                outcome = blockchain.add_block(data)
                if (outcome == True):
                    print(f"Removed item {args.item_id} from the blockchain.")
                else: 
                    print("Block remove failed")
            else:
                print("Item ID is required for 'remove' action.")

        elif args.action == 'init':
            # initial = blockchain._check_for_initial()
            # if initial == True:
            #     print("Initialized a new blockchain.")
            # else : 
            #     print("Blochain initialization failed")
            blockchain.init()
        # Optionally, you might want to handle initialization logic here.
        #checks for initial block to verify blokchain is setup properly

        elif args.action == 'verify':
            blockchain._verify_checksums()

        else :
            print("invalid command")
    

def verify_blockchain_integrity(blockchain, password):
    # Example: Perform integrity verification logic based on the password
    # You may want to implement more sophisticated integrity checks.
    return True

if __name__ == "__main__":
    main()