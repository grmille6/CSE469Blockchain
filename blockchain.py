import hashlib
import json
import time

class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = hash

def calculate_hash(index, previous_hash, timestamp, data):
    hash_string = f"{index}{previous_hash}{timestamp}{json.dumps(data)}"
    return hashlib.sha256(hash_string.encode()).hexdigest()

def create_genesis_block():
    return Block(0, "0", time.time(), "Genesis Block", calculate_hash(0, "0", time.time(), "Genesis Block"))

def create_new_block(previous_block, data):
    index = previous_block.index + 1
    timestamp = time.time()
    hash_value = calculate_hash(index, previous_block.hash, timestamp, data)
    return Block(index, previous_block.hash, timestamp, data, hash_value)

class Blockchain:
    def __init__(self):
        self.chain = [create_genesis_block()]

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        new_block = create_new_block(self.get_latest_block(), data)
        self.chain.append(new_block)

# Example usage
blockchain = Blockchain()

# Adding blocks to the blockchain
blockchain.add_block({"evidence": "file1.txt", "action": "collected", "by": "investigator1"})
blockchain.add_block({"evidence": "file1.txt", "action": "transferred", "to": "forensic_lab"})
blockchain.add_block({"evidence": "file1.txt", "action": "analyzed", "by": "analyst1"})

# Print the blockchain
for block in blockchain.chain:
    print(f"Block {block.index} - Hash: {block.hash}")
    print("Timestamp:", block.timestamp)
    print("Data:", block.data)
    print("Previous Hash:", block.previous_hash)
    print("\n")
