from bitcoin_rpc import rpc_call
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


"""
Prints stats about the occupancy of blocks between the two given blockheights.
"""

progress_lock = threading.Lock()
progress_counter = 0


def parse_block(height, total_blocks):
    global progress_counter
    try:
        blockhash = rpc_call("getblockhash", [height])
        block = rpc_call("getblock", [blockhash, 1])
        weight = block.get('weight', 0)

        with progress_lock:
            progress_counter += 1
            print(f"Progress: {progress_counter}/{total_blocks} blocks processed", end='\r')

        return weight
    except Exception as e:
        print(f"Error processing block {height}: {e}")
        return 0

def main(start_height, end_height, max_workers=8):
    global progress_counter
    total_blocks = end_height - start_height + 1
    all_weights = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(parse_block, height, total_blocks): height for height in range(start_height, end_height + 1)}
        for future in as_completed(futures):
            weight = future.result()
            all_weights.append(weight)

    occupancy_percentages = [(w / 4_000_000) * 100 for w in all_weights if w > 0]

    if occupancy_percentages:
        average_occupancy = sum(occupancy_percentages) / len(occupancy_percentages)
        print(f"\n\nAverage block occupancy between heights {start_height} and {end_height}: {average_occupancy:.2f}%")

        buckets = {'0-25%': 0, '25-50%': 0, '50-75%': 0, '75-100%': 0}
        for occ in occupancy_percentages:
            if occ < 25:
                buckets['0-25%'] += 1
            elif occ < 50:
                buckets['25-50%'] += 1
            elif occ < 75:
                buckets['50-75%'] += 1
            else:
                buckets['75-100%'] += 1

        print("\nOccupancy distribution:")
        for range_label, count in buckets.items():
            print(f"  {range_label}: {count} blocks")
    else:
        print("\n\nNo valid blocks found.")

if __name__ == "__main__":
    main(start_height=800000, end_height=800010, max_workers=16)
