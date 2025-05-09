from bitcoin_rpc import rpc_call
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


"""
Prints stats about OP_RETURN txs found between the two given block heights.
It counts how many OP_RETURNs are larger than 83 bytes, and how many OP_RETURN
outputs there are in each tx with at least 1 of them.
"""

progress_lock = threading.Lock()
progress_counter = 0


def parse_block(height, total_blocks):
    global progress_counter
    try:
        blockhash = rpc_call("getblockhash", [height])
        block = rpc_call("getblock", [blockhash, 2])

        size_buckets = {'<=83': 0, '>83': 0}
        tx_opreturn_counts = defaultdict(int)

        for tx in block['tx']:
            if tx['vin'][0].get('coinbase') is not None:
                continue  # Ignore coinbase txs
            opreturn_count = 0

            for vout in tx['vout']:
                script = vout['scriptPubKey'].get('hex', '')
                if script.startswith('6a'):
                    size = int(len(script)/2)
                    if size <= 83:
                        size_buckets['<=83'] += 1
                    else:
                        size_buckets['>83'] += 1
                    opreturn_count += 1

            if opreturn_count > 0:
                tx_opreturn_counts[opreturn_count] += 1

        with progress_lock:
            progress_counter += 1
            print(f"Progress: {progress_counter}/{total_blocks} blocks processed", end='\r')

        return size_buckets, tx_opreturn_counts
    except Exception as e:
        print(f"Error processing block {height}: {e}")
        return {'<=83': 0, '>83': 0}, defaultdict(int)

def main(start_height, end_height, max_workers=8):
    global progress_counter
    total_size_buckets = {'<=83': 0, '>83': 0}
    total_tx_opreturn_counts = defaultdict(int)
    total_blocks = end_height - start_height + 1

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(parse_block, height, total_blocks): height for height in range(start_height, end_height + 1)}
        for future in as_completed(futures):
            size_buckets, tx_opreturn_counts = future.result()
            for k in total_size_buckets:
                total_size_buckets[k] += size_buckets[k]
            for count, qty in tx_opreturn_counts.items():
                total_tx_opreturn_counts[count] += qty

    print("\n\nOP_RETURN size buckets:")
    for bucket, count in total_size_buckets.items():
        print(f"  {bucket}: {count}")

    print("\nTransactions by number of OP_RETURNs (excluding coinbase):")
    for count in sorted(total_tx_opreturn_counts):
        print(f"  {count} OP_RETURN(s): {total_tx_opreturn_counts[count]} transactions")

if __name__ == "__main__":
    main(start_height=800000, end_height=800010, max_workers=16)
