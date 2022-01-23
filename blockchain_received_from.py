"""This script will take one Bitcoin address and a level as arguments.
It will try to print all the addresses that have sent bitcoin to that
address, to the given level
"""

from argparse import ArgumentParser
from datetime import datetime
from time import time
from typing import List, Any
from blockchain import blockexplorer


def gather_inputs(address: str, depth: int) -> List[Any]:
    """Gather all inputs spent from the address up to the specified
    depth.
    """
    all_adr = []
    for i in range(0, depth+1):
        all_adr.append([])
    all_adr[0] = [[address, int(round(time())), 0]]
    for i in range(depth):
        for j in range(len(all_adr[i])):
            cur_adr = all_adr[i][j][0]
            cur_time = all_adr[i][j][1]
            outs = get_in_addr(cur_adr, cur_time, j)
            all_adr[i+1] = all_adr[i+1] + outs
    return all_adr


def get_in_addr(address: str, txtime: int, prev_index: int) -> List[Any]:
    """Find all addresses that have received bitcoin from a given
    address after the given time. The argument prev_index is used to
    keep track of the index of the connected address at the previous
    level.
    """
    outs = []
    startaddress = blockexplorer.get_address(address)
    for curtx in startaddress.transactions:
        flag = False
        for curin in curtx.outputs:
            # print(f"Testing1: {curin.address} {address}")
            # print(f"Testing2: {curtx.time} {txtime}")
            if (curin.address == address) and (curtx.time < txtime):
                flag = True
        if flag:
            for curadr in curtx.inputs:
                # API does not support Bech32 addresses
                if curadr.address[:3] != "bc1":
                    outs.append([curadr.address, curtx.time, prev_index])
    return outs


def nice_print(array):
    """Print the addresses in the array with level
    """
    for i, outer_value in enumerate(array):
        print(f"Depth: {i} has {len(outer_value)} matches")
        print(f"Level: {i}")
        for inner_value in outer_value:
            print(f"Address: {inner_value[0]}, " +
                  f"Date/time: {datetime.fromtimestamp(inner_value[1])}, " +
                  f"Previous level index: {inner_value[2]}"
                  )
    return 0


def trace_back(array, i, j):
    """Trace all addresses back to the original.
    """
    level = i
    sublevel = j
    while level > 0:
        sublevel = array[level][sublevel][2]
        level = level-1
        print(array[level][sublevel])


def main():
    """Get address and depth from arguments, call the gather_inputs
    function and print the results.
    """
    parser = ArgumentParser()
    parser.add_argument("firstaddr", help="The receiving address")
    parser.add_argument("depth", help="The depth of the search")
    args = parser.parse_args()
    print("Searching blockchain ...")
    adr = args.firstaddr
    depth = int(args.depth)
    all_adr = gather_inputs(adr, depth)
    nice_print(all_adr)


if __name__ == "__main__":
    main()
