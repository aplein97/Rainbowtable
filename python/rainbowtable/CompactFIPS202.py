# -*- coding: utf-8 -*-
# From https://github.com/XKCP/XKCP/blob/715fbb4d654b474eecc0706ee7efffaebeda4258/Standalone/CompactFIPS202/Python/CompactFIPS202.py
#
# Implementation by Gilles Van Assche, hereby denoted as "the implementer".
#
# For more information, feedback or questions, please refer to our website:
# https://keccak.team/
#
# To the extent possible under law, the implementer has waived all copyright
# and related or neighboring rights to the source code in this file.
# http://creativecommons.org/publicdomain/zero/1.0/

def ROL64(a, n):
    return ((a >> (64-(n%64))) + (a << (n%64))) % (1 << 64)


def KeccakF1600onLanes(lanes):
    R = 1
    for round in range(24):
        # θ
        C = [lanes[x][0] ^ lanes[x][1] ^ lanes[x][2] ^ lanes[x][3] ^ lanes[x][4] for x in range(5)]
        D = [C[(x+4)%5] ^ ROL64(C[(x+1)%5], 1) for x in range(5)]
        lanes = [[lanes[x][y]^D[x] for y in range(5)] for x in range(5)]
        # ρ and π
        (x, y) = (1, 0)
        current = lanes[x][y]
        for t in range(24):
            (x, y) = (y, (2*x+3*y)%5)
            (current, lanes[x][y]) = (lanes[x][y], ROL64(current, (t+1)*(t+2)//2))
        # χ
        for y in range(5):
            T = [lanes[x][y] for x in range(5)]
            for x in range(5):
                lanes[x][y] = T[x] ^((~T[(x+1)%5]) & T[(x+2)%5])
        # ι
        for j in range(7):
            R = ((R << 1) ^ ((R >> 7)*0x71)) % 256
            if (R & 2):
                lanes[0][0] = lanes[0][0] ^ (1 << ((1<<j)-1))
    return lanes


def load64(b):
    return sum((b[i] << (8*i)) for i in range(8))


def store64(a):
    return list((a >> (8*i)) % 256 for i in range(8))


def KeccakF1600(state):
    lanes = [[load64(state[8*(x+5*y):8*(x+5*y)+8]) for y in range(5)] for x in range(5)]
    lanes = KeccakF1600onLanes(lanes)
    state = bytearray(200)
    for x in range(5):
        for y in range(5):
            state[8*(x+5*y):8*(x+5*y)+8] = store64(lanes[x][y])
    return state


def Keccak(rate, capacity, inputBytes: bytearray, delimitedSuffix, outputByteLen: int):
    outputBytes = bytearray()
    state = bytearray([0 for i in range(200)])
    rateInBytes = rate//8
    blockSize = 0
    if (((rate + capacity) != 1600) or ((rate % 8) != 0)):
        return
    inputOffset = 0
    # === Absorb all the input blocks ===
    while(inputOffset < len(inputBytes)):
        blockSize = min(len(inputBytes)-inputOffset, rateInBytes)
        for i in range(blockSize):
            state[i] = state[i] ^ inputBytes[i+inputOffset]
        inputOffset = inputOffset + blockSize
        if (blockSize == rateInBytes):
            state = KeccakF1600(state)
            blockSize = 0
    # === Do the padding and switch to the squeezing phase ===
    state[blockSize] = state[blockSize] ^ delimitedSuffix
    if (((delimitedSuffix & 0x80) != 0) and (blockSize == (rateInBytes-1))):
        state = KeccakF1600(state)
    state[rateInBytes-1] = state[rateInBytes-1] ^ 0x80
    state = KeccakF1600(state)
    # === Squeeze out all the output blocks ===
    while(outputByteLen > 0):
        blockSize = min(outputByteLen, rateInBytes)
        outputBytes = outputBytes + state[0:blockSize]
        outputByteLen = outputByteLen - blockSize
        if (outputByteLen > 0):
            state = KeccakF1600(state)
    return outputBytes


def SHAKE128(inputBytes, outputByteLen) -> bytearray:
    return Keccak(1344, 256, inputBytes, 0x1F, outputByteLen)


def SHAKE256(inputBytes, outputByteLen) -> bytearray:
    return Keccak(1088, 512, inputBytes, 0x1F, outputByteLen)


def SHA3_224(inputBytes: bytearray) -> bytearray:
    return Keccak(1152, 448, inputBytes, 0x06, 224//8)


def SHA3_256(inputBytes: bytearray) -> bytearray:
    return Keccak(1088, 512, inputBytes, 0x06, 256//8)


def SHA3_384(inputBytes: bytearray) -> bytearray:
    return Keccak(832, 768, inputBytes, 0x06, 384//8)


def SHA3_512(inputBytes: bytearray) -> bytearray:
    return Keccak(576, 1024, inputBytes, 0x06, 512//8)


# If executed directly, runs a comparison in runtime between different SHA-3 hashes.
if __name__ == "__main__":
    import random
    import string
    import time

    # Generate a few random strings.
    str_length = 20
    str_count = 10**5
    print(f"Compare hashing of {str_count} strings with {str_length} chars each")

    strings = []
    for _ in range(str_count):
        strings.append(
            bytes(
                ''.join(random.choices(string.ascii_uppercase + string.digits, k=str_length)),
                'ascii'
            )
        )

    # SHA3-512
    start = time.time()
    for plaintext in strings:
        SHA3_512(plaintext)
    end = time.time()

    print(f"SHA3-512 {end - start}s")

    # SHA3-256
    start = time.time()
    for plaintext in strings:
        SHA3_256(plaintext)
    end = time.time()

    print(f"SHA3-256 {end - start}s")
