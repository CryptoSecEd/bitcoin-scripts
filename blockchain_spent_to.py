"""This script will take one Bitcoin address and a level as arguments.
It will try to print all the addresses that have received bitcoin from
that address, to the given level.
"""

from argparse import ArgumentParser
from datetime import datetime
from blockchain import blockexplorer


def gather_outputs(address, depth):
    """Gather all outputs spent from the address up to the specified
    depth
    """
    all_adr = []
    for i in range(0, depth+1):
        all_adr.append([])
    all_adr[0] = [[address, 0, 0]]
    for i in range(depth):
        for j in range(len(all_adr[i])):
            cur_adr = all_adr[i][j][0]
            cur_time = all_adr[i][j][1]
            outs = get_out_addr(cur_adr, cur_time, j)
            all_adr[i+1] = all_adr[i+1] + outs
    return all_adr


def get_out_addr(address, txtime, prev_level):
    """Find all addresses that have sent bitcoin to a given address
    after the given time. The argument prev_index is used to keep track
    of the index of the connected address at the previous level.
    """
    outs = []
    startaddress = blockexplorer.get_address(address)
    for curtx in startaddress.transactions:
        flag = False
        for curin in curtx.inputs:
            if ((hasattr(curin, 'address')) and (curin.address == address)
                    and (curtx.time > txtime)):
                flag = True
        if flag:
            for curadr in curtx.outputs:
                # print(curadr.address)
                # API does not support Bech32 addresses
                if ((curadr.address is not None)
                        and (curadr.address[:3] != "bc1")):
                    outs.append([curadr.address, curtx.time, prev_level])
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
    """Get address and depth from arguments, call the gather_outputs
    function and print the results.
    """
    parser = ArgumentParser()
    parser.add_argument("firstaddr", help="The sending address")
    parser.add_argument("depth", help="The depth of the search")
    args = parser.parse_args()
    print("Seaching blockchain ...")
    adr = args.firstaddr
    depth = int(args.depth)
    all_adr = gather_outputs(adr, depth)
    nice_print(all_adr)


if __name__ == "__main__":
    main()
