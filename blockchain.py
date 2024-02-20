import os
import struct
from enum import Enum
from datetime import datetime, timezone
import hashlib
from uuid import UUID
from enum import Enum
import sys

class State(Enum):
    INITIAL = "INITIAL"
    CHECKED_IN = "CHECKEDIN"
    CHECKED_OUT = "CHECKEDOUT"
    DISPOSED = "DISPOSED"
    DESTROYED = "DESTROYED"
    RELEASED = "RELEASED"
    
class Blockchain:

    RECORD_SIZE = 144
                
    def _write_starting_block(self):
        """
        Writes the initial block when the new file is created
        """
        
        file_path = os.getenv("BCHOC_FILE_PATH", "C:\\Projects\\CSE469 Project\\CSE469\\chain.dat")

        try:
            with open(file_path, 'rb') as f:
                if f.read(): #File has content
                    return
        except FileNotFoundError:
            pass #File does not exist, will be created
        
            # Define initial block values
            previous_hash = b'\x00' * 32  # 32 bytes of zeros for initial block
            timestamp = datetime.now(timezone.utc).timestamp() #timestamp = 0
            case_id = b'\x00' * 32  # Placeholder for initial block
            item_id = b'\x00' * 32  # Placeholder for initial block
            state = 'INITIAL'.ljust(12, '\x00').encode()  # Padded to 12 bytes
            creator = b'\x00' * 12  # Placeholder for initial block
            owner = b'\x00' * 12  # Placeholder for initial block
            data = 'Initial block'.encode()
            data_length = len(data)
            
            # Pack the block using struct
            block_format = '32s d 32s 32s 12s 12s 12s I {}s'.format(data_length)
            block_data = struct.pack(block_format, previous_hash, timestamp, case_id, item_id, state, creator, owner, data_length, data)

            # Write the initial block to the file
            with open(file_path, 'wb') as f:
                f.write(block_data)

    def _read_blocks(self):
        """"
        Returns a list of dictionaries representing blocks.
        The following fields are present:
            - previous_hash: a hex string containing the hash of the previous block
            - timestamp: a datetime object containing the UTC-based time of writing
            - case_id: a UUID object representing ID of the case
            - item_id: an integer representing ID of an item
            - state: a string following the convention of the State enum
            - data_length: length of the description area, stored as integer
            - data: a string of defined length
        """
        file_path = os.getenv("BCHOC_FILE_PATH", "C:\\Projects\\CSE469 Project\\CSE469\\chain.dat")
        blocks = []
        
        try:
            with open(file_path, 'rb') as f:
                while True:
                    #Read the block header to get the data length
                    header_format = '32s d 32s 32s 12s 12s 12s I'
                    header_size = struct.calcsize(header_format)
                    header_data = f.read(header_size)
                    
                    if not header_data:
                        break #End of file reached
                    
                    #Unpack the header
                    previous_hash, timestamp, case_id, item_id, state, creator, owner, data_length = struct.unpack(header_format, header_data)
                    
                    #Read the data field based on the data_length
                    data_format = '{}s'.format(data_length)
                    data = f.read(data_length)
                    data = struct.unpack(data_format, data)[0].decode('utf-8')
                    
                    #Convert fields to appropriate types
                    previous_hash = previous_hash.hex()
                    timestamp = datetime.utcfromtimestamp(timestamp)
                    case_id = UUID(bytes=case_id)
                    item_id = int.from_bytes(item_id, byteorder=sys.byteorder)
                    state = state.decode('utf-8').strip('\x00')
                    
                    #Append the block to the blocks list
                    blocks.append({
                        'previous_hash': previous_hash,
                        'timestamp': timestamp,
                        'case_id': case_id,
                        'item_id': item_id,
                        'state': state,
                        'data_length': data_length,
                        'data': data,
                        })
        except FileNotFoundError:
            print("Blockchain file not found.")
        
        return blocks
    
    def _get_specific_block(self, item_id):
        """
        Returns a dictionary rep of the block
        """
        for block in reversed(self._read_blocks()):
            if block['item_id'] == item_id:
                return block
        return None
        
    def _write_block(
            self,
            case_id: UUID,
            item_id: int,
            state: str,
            data: str
            ):
        
        file_path = os.getenv("BCHOC_FILE_PATH", "C:\\Projects\\CSE469 Project\\CSE469\\chain.dat")
        
        #Convert inputs to correct format
        case_id_bytes = case_id.bytes
        item_id_bytes = item_id.to_bytes(4, byteorder = sys.byteorder)
        state_bytes = state.ljust(12, '\x00').encode()
        data_bytes = data.encode()
        data_length = len(data_bytes)
        
        #Calculate the previous block's hash
        previous_hash = self._calculate_previous_hash(file_path)
        
        #Current UTC time
        timestamp = datetime.utcnow().timestamp()
        
        #Pack the block using struct
        block_format = '32s d 32s 32s 12s 12s 12s I {}s'.format(data_length)
        block_data = struct.pack(block_format, previous_hash, timestamp, case_id_bytes, item_id_bytes, state_bytes, b'\x00'*12, b'\x00'*12, data_length, data_bytes)
        
        #Write the block to the file
        try:
            with open(file_path, 'ab') as f: #Open the file in append-binary mode
                f.write(block_data)
            return True
        except Exception as e:
            print(f"Failed to write block: {e}")
            return False

    def _calculate_previous_hash(self, file_path):
        """
        Calculate the hash of the last block in the file
        """
        try:
            with open(file_path, 'rb') as f:
                f.seek(0, os.SEEK_END)
                filesize = f.tell()
                if filesize == 0:
                    return b'\x00' * 32 #If the file is empty, return 32 bytes of zeros
                
                f.seek(-1, os.SEEK_END)
                while f.read(1) != b'\x00':
                    f.seek(-2, os.SEEK_CUR)
                    
                last_block_start = f.tell() + 1
                f.seek(last_block_start)
                last_block = f.read()

                #Calculate and return the hash
                return hashlib.sha256(last_block).digest()
            
        except FileNotFoundError:
            return b'\x00' * 32 #If the file does not exist, return 32 bytes of zeros
        
    def _check_for_initial(self):
        """
        Checks for an INITIAL block within the chain.
        :return: True if an INITIAL block is found, False otherwise.
        """
        # Use the _read_blocks method to get all blocks
        blocks = self._read_blocks()

        # Iterate through each block and check its state
        for block in blocks:
            if block['state'] == 'INITIAL':
                return True  # Return True immediately if an INITIAL block is found

        # If the loop completes without finding an INITIAL block, return False
        return False

    def _calculate_block_hash(self, block):
        """
        Calculates the SHA-256 hash of the given block.
        :param block: A dictionary representing a block with keys for previous hash, timestamp,
                      case ID, item ID, state, and data.
        :return: A hex string representing the hash of the block.
        """
        # Create a string representation of the block.
        block_string = f"{block['previous_hash']}{block['timestamp']}{block['case_id']}{block['item_id']}{block['state']}{block['data_length']}{block['data']}"
    
        # Encode the string to a byte array
        block_encoded = block_string.encode()

        # Calculate the SHA-256 hash of the encoded block
        block_hash = hashlib.sha256(block_encoded).hexdigest()

        return block_hash

    def _verify_checksums(self):
        """
        Performs verification of the blockchain to check for integrity issues.
        :return: A tuple containing:
            - An integer: the number of blocks checked,
            - A string: error type ("NO PARENT", "DUPLICATE PARENT", "IMPROPER REMOVAL", or "VALID" if no errors),
            - A hash (or list of hashes in case of "DUPLICATE PARENT"): blocks involved in the error.
        """
        # Initially, assume blockchain is valid
        error = "VALID"
        error_hashes = []

        # Use the _read_blocks method to get all blocks
        blocks = self._read_blocks()

        # Dictionary to track parent blocks
        parent_blocks = {}

        for i, block in enumerate(blocks):
            # Skip the initial block as it has no parent
            if i == 0:
                continue

            prev_hash = block['previous_hash']
            current_hash = self._calculate_block_hash(block)  # You need to implement this method

            # Check for "NO PARENT"
            if prev_hash not in parent_blocks and i != 0:
                error = "NO PARENT"
                error_hashes.append(current_hash)
                break

            # Check for "DUPLICATE PARENT"
            if prev_hash in parent_blocks:
                error = "DUPLICATE PARENT"
                error_hashes.extend([parent_blocks[prev_hash], current_hash])
                break

            parent_blocks[prev_hash] = current_hash

            # Additional checks can be implemented here, such as "IMPROPER REMOVAL", not usre how yet though
            #This might be a TODO

        # Determine the number of transactions (blocks) checked
        num_transactions = len(blocks)

        # Depending on your blockchain's structure, you may need to adjust how errors are detected and how hashes are calculated or stored.
        return num_transactions, error, error_hashes

    def _verify_remove_is_final(self):
        """
        Loops through the entire blockchain, keeping track of all items that have been removed. If an item that has been removed appears again, return False.
        Otherwise, return True.
        """
        # Use the _read_blocks method to get all blocks
        blocks = self._read_blocks()

        # Keep track of item IDs and their removal status
        removed_items = set()
        seen_items = set()

        for block in blocks:
            item_id = block['item_id']  # Assuming this gets the item ID correctly
            state = block['state']

            # Check if the item has been marked as removed
            if state in ["DISPOSED", "DESTROYED", "RELEASED"]:
                if item_id in removed_items:
                    # Item was removed before, should not appear again
                    continue  # might log a warning here. I have not implemented this yet though
                removed_items.add(item_id)

            if item_id in seen_items and item_id in removed_items:
                # If an item that was previously removed is seen again, return False
                return False
            else:
                seen_items.add(item_id)

        # If the loop completes without finding any items that reappear after removal, return True
        return True

    def _verify_add_is_first(self):
        """
        Loops through the entire blockchain, checking every new item. If a new item has the status 'CHECKEDIN', then continue. If a new item has any other status, return False.
        Once the end of the chain has been reached with no returns, return True.
        """
        # Use the _read_blocks method to get all blocks
        blocks = self._read_blocks()

        # Keep track of the item IDs that have been encountered
        encountered_items = {}

        for block in blocks:
            item_id = block['item_id']  # Assuming this gets the item ID correctly
            state = block['state']

            # Check if the item is encountered for the first time
            if item_id not in encountered_items:
                # If the item's first state is not 'CHECKEDIN', return False
                if state != 'CHECKEDIN':
                    return False
                encountered_items[item_id] = True
            # No need to check further if the item has already been encountered

        # If the loop completes without encountering any item that violates the rule, return True
        return True

    def _verify_all_released(self):
        """
        Loops through the blockchain, makes sure that the releases are valid
        """
        blocks = self._read_blocks()
        
        for block in blocks:
            if block['state'] == "RELEASED" and block['data_length'] <= 0:
                return False
            
        return True
    
    def _check_double_check(self):
        """
        Loops through the entire blockchain. Checks if any item is checked out twice 
        with no checkins inbetween, and if any item is checked in twice with no checkouts
        inbetween. Returns false if that does so happen to happen
        """
        # Use the _read_blocks method to get all blocks
        blocks = self._read_blocks()

        # Keep track of the last state for each item
        last_state = {}

        for block in blocks:
            item_id = block['item_id']  # Assuming this gets the item ID correctly
            state = block['state']

            # Check conditions for CHECKEDOUT and CHECKEDIN states
            if state == 'CHECKEDOUT':
                if item_id in last_state and last_state[item_id] == 'CHECKEDOUT':
                    # Item is checked out again without being checked in
                    return False
            elif state == 'CHECKEDIN':
                if item_id in last_state and last_state[item_id] == 'CHECKEDIN':
                    # Item is checked in again without being checked out
                    return False
        
            # Update the last state for the item
            last_state[item_id] = state

        # If the loop completes without finding any violations, return True
        return True
    
    def _unique_parent_check(self):
        """
        This checks if any block shares a parent with another and reutnrs false if it does
        """
        blocks = self._read_blocks()
        
        parents = []
        
        for block in blocks:
            parent = block['previous_hash']
            
            if parent in parents:
                return False
            else:
                parent.append(block['previous_hash'])
                
        return True

    def _get_last_block(self):
        """
        Retrieves the last block from the blockchain file.
        """
        file_path = os.getenv('BCHOC_FILE_PATH', 'default_blockchain_file_path.dat')
        blocks = self._read_blocks()

        if blocks:
            return blocks[-1]  # Return the last block if available
        else:
            return None  # Return None if the blockchain is empty

    def _get_last_hash(self):
        """
        Calculates hash of the last block, used when a previously created file is read.
        """
        # Use a modified version of _read_blocks method to get the last block only
        last_block = self._get_last_block()

        if last_block is None:
            return None  # Return None if there are no blocks
    
        last_block_hash = self._calculate_block_hash(last_block)

        return last_block_hash

    def __init__(self):
        """
        Creates the INITIAL block
        """
        file_path = os.getenv("BCHOC_FILE_PATH", "C:\\Projects\\CSE469 Project\\CSE469\\chain.dat")

        if not os.path.isfile(self.file_path):
            self._write_starting_block()
        #If there is already something go get it
        elif self._check_for_initial():
            self.previous_hash = self._get_last_hash()
