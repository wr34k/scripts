#!/usr/bin/env python3

import os
from argparse import ArgumentParser
from binascii import hexlify, unhexlify

CHARS=[
    "abcdefghijklmnopqrstuvwxyz",
    "0123456789",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "abcdefghijklmnopqrstuvwxyz"
]
PATTERN_LIMIT = 10000000


def get_ascii_pattern(pattern):
    pattern=pattern.replace("\\x", "")
    try:
        ret=unhexlify(pattern)
    except:
        ret=pattern.encode('ascii')
        pass

    return str(ret, 'ascii')

def get_pattern(**kwargs):
    if not 'length' in kwargs \
        and not 'offset' in kwargs:
        return None

    retLength = kwargs['length'] if 'length' in kwargs else None
    offset = kwargs['offset'] if 'offset' in kwargs else None
    ret=""
    rnd=0
    i=[0 for _ in range(len(CHARS))]

    while True:

        ret+=CHARS[rnd%len(CHARS)][i[rnd%len(CHARS)]]
        rnd+=1

        if retLength:
            if rnd == retLength:
                break

        if rnd%len(CHARS) == 0:
            for j in range(len(CHARS)-1, 0, -1):
                i[j]+=1
                if i[j] < len(CHARS[j]):
                    break
                i[j]=0

        if offset:
            if len(ret) >= len(offset):
                if ret[(len(offset)*-1):] == offset:
                    ret = f"Pattern found at offset {rnd-len(offset)}"
                    break

        if rnd >= PATTERN_LIMIT:
            ret = None
            break

    return ret


def get_args():
    p = ArgumentParser(description="Create a rettern to facilitate exploit dev")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("-c", "--create", help="Create a new rettern", type=int)
    g.add_argument("-o", "--offset", help="Get the offset of a rettern", type=str)

    return p.parse_args()

def inverse_endianness(pattern):
    return pattern[::-1]

def main():
    args = get_args()

    if args.create:
        ret=get_pattern(length=args.create)

    elif args.offset:
        pat=get_ascii_pattern(args.offset)
        ret=get_pattern(offset=pat)

        if not ret:
            pat=inverse_endianness(pat)
            ret=get_pattern(offset=pat)

        if not ret:
            pat=inverse_endianness(pat)
            print(f"Pattern {pat} not found in the first {PATTERN_LIMIT} characters...")
            return

    if os.fstat(0) == os.fstat(1):
        print(ret)
    else:
        print(ret, end="")

        return 0

if __name__=='__main__':
    exit(main())
