from bitcoin_rpc import rpc_call
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


"""
Prints how many P2MS outputs exist between two given blockheights,
and how many txs contain them.
"""

progress_lock = threading.Lock()
progress_counter = 0


def parse_block(height, total_blocks):
    global progress_counter
    try:
        blockhash = rpc_call("getblockhash", [height])
        block = rpc_call("getblock", [blockhash, 2])

        bare_multisig_txs = 0
        bare_multisig_outputs = 0

        for tx in block['tx']:
            if tx['vin'][0].get('coinbase') is not None:
                continue  # Ignore coinbase txs

            has_p2ms = False
            for vout in tx['vout']:
                if vout['scriptPubKey'].get('type', '') == 'multisig':
                    has_p2ms = True
                    bare_multisig_outputs += 1

            if has_p2ms:
                bare_multisig_txs += 1

        with progress_lock:
            progress_counter += 1
            print(f"Progress: {progress_counter}/{total_blocks} blocks processed", end='\r')

        return bare_multisig_outputs, bare_multisig_txs
    except Exception as e:
        print(f"Error processing block {height}: {e}")
        return {'<=83': 0, '>83': 0}, defaultdict(int)

def main(start_height, end_height, max_workers=8):
    global progress_counter
    total_bare_multisig_txs = 0
    total_bare_multisig_outputs = 0
    total_blocks = end_height - start_height + 1

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(parse_block, height, total_blocks): height for height in range(start_height, end_height + 1)}
        for future in as_completed(futures):
            bare_multisig_outputs, bare_multisig_txs = future.result()
            total_bare_multisig_outputs += bare_multisig_outputs
            total_bare_multisig_txs += bare_multisig_txs

    print("\n\nTotal P2MS Outputs:")
    print(f"  {total_bare_multisig_outputs}")

    print("\nTotal Transactions with a P2MS Outputs:")
    print(f"  {total_bare_multisig_txs}")


if __name__ == "__main__":
    main(start_height=896000, end_height=896012, max_workers=1)
