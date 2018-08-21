#!/usr/bin/env python3

import sys

CAVE_MIN_SIZE = 64

phex = lambda x: "0x" + f"{x:x}".upper()

def printCave(start, end):
    print(f"[*] Cave found from offset {phex(start)} to {phex(end)} (size: {end-start} B) ...")

def main():
    bin_path = sys.argv[1]

    with open(bin_path, "rb") as f:
        bin_data = f.read()

    is_in_cave = False
    cave_start = 0
    for i in range(len(bin_data)):
        if bin_data[i] != 0x00:
            if is_in_cave:
                is_in_cave = False
                if (i-1) - cave_start >= CAVE_MIN_SIZE:
                    printCave(cave_start, i-1)
            continue

        if not is_in_cave:
            is_in_cave = True
            cave_start = i

if __name__=='__main__':
    main()
