# OP_RETURN and Block Occupancy stats

## Usage

Edit `RPC_USER`, `RPC_PASSWORD` and `RPC_URL` in bitcoin_rpc.py as needed.
Edit `start_height` and `end_height` as desired in occupancy.py and opreturns.py.

```shell
$ python baremulti.py
$ python occupancy.py
$ python opreturns.py
```

## Requirements

* Python +3.10
* Unpruned Bitcoin Core or Bitcoin Knots node with RPC enabled


## Performance Tuning

Set `max_workers` in occupancy.py and opreturns.py to match the number of cores in your machine.

The bottleneck of the scripts are its I/O operations.
It's recommended to run them in the same machine as the node to avoid network traffic.

It's also helpful if the node machine has fast storage (NVME SSD) and lots of CPU cores.
You can bump Core/Knots `rpcthreads` setting to match the number of cores in your machine (default value is only 4).


## Reference block dates

| Date       | Block Height |
|------------|--------------|
| 2022-01-01 | 716695       |
| 2023-01-01 | 769873       |
| 2024-01-01 | 823866       |
| 2025-01-01 | 877325       |
| 2025-04-26 | 894055       |
