#!/usr/bin/env python3

import sys

def main(argv):
    if len(argv) <= 1:
        print("Usage: python3 {} <file to fix>".format(argv[0]))
        exit()

    with open(argv[1], "r") as f:
        data = f.read()
    data = data.replace("\t", "    ")
    with open(argv[1], "w") as f:
        f.write(data)
    print("done")

    return 0

if __name__=='__main__':
    exit(main(sys.argv))
