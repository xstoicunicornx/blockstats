from bitcoin_rpc import rpc_call
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import csv

"""
Prints stats about OP_RETURN txs found between the two given block heights.
It saves a list of all transactions that contain OP_RETURN to the indicated
file. Data saved for each tx includes:
- block height
- blockhash
- tx id
- OP_RETURN count
- OP_RETURN size
"""

START_HEIGHT = 903000
STOP_HEIGHT = 903879
FILE_NAME = "opreturn_data.csv"

progress_lock = threading.Lock()
progress_counter = 0


def parse_block(height, total_blocks):
    global progress_counter
    try:
        blockhash = rpc_call("getblockhash", [height])
        block = rpc_call("getblock", [blockhash, 2])

        data = []

        for tx in block['tx']:
            if tx['vin'][0].get('coinbase') is not None:
                continue  # Ignore coinbase txs

            has_opreturn = False
            opreturn_count = 0
            opreturn_size = 0
            for vout in tx['vout']:
                script = vout['scriptPubKey'].get('hex', '')
                if script.startswith('6a'):
                    if not has_opreturn:
                        has_opreturn = True
                    size = int(len(script)/2)
                    opreturn_count += 1
                    opreturn_size += size
            if has_opreturn:
                data.append([height, blockhash, tx['txid'], opreturn_count, opreturn_size])

        with progress_lock:
            progress_counter += 1
            print(f"Progress: {progress_counter}/{total_blocks} blocks processed", end='\r')

        return data
    except Exception as e:
        print(f"Error processing block {height}: {e}")
        return []

def main(start_height, end_height, max_workers=8):
    global progress_counter
    total_blocks = end_height - start_height + 1
    data = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(parse_block, height, total_blocks): height for height in range(start_height, end_height + 1)}
        for future in as_completed(futures):
            data += future.result()

    print(f"\n\nOP_RETURN txs found: {len(data)}")

    print(f"\nSaving data to {FILE_NAME}")
    with open('some.csv', 'w', newline='') as f:
        writer = csv.writer(open("./"+FILE_NAME, 'w'))
        writer.writerows(data)


if __name__ == "__main__":
    main(start_height=800000, end_height=800010, max_workers=16)
