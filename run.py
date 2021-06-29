import hashlib
import random
import string
import time
from typing import List

from rainbowtable import RainbowTable, reduction_function1


length = 8
iterations = 1000
rows = 100


def reduction_fn(hash_str: str, index: int) -> str:
    return reduction_function1(hash_str=hash_str, length=length, index=index)


def hash_fn(plain_str: str) -> str:
    return hashlib.sha3_224(plain_str.encode('ascii')).hexdigest()[:length]
    # return hashlib.md5(plain_str.encode('ascii')).hexdigest()[:length]
    # return hashlib.md5(plain_str.encode('ascii')).hexdigest()


def generate_plaintext() -> str:
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def load_wordlist(filename: str) -> List[str]:
    return [word.strip() for word in open(filename, 'r').readlines()]


def test_fill(concurrent: bool) -> RainbowTable:
    wordlist = [generate_plaintext() for _ in range(0, rows)]
    r = RainbowTable(iterations=iterations, reduction_fn=reduction_fn, hash_fn=hash_fn)

    start = time.time()
    r.fill(wordlist=wordlist, concurrent=concurrent)
    end = time.time()

    print("Finished filling {} rows in {:0.3f} seconds (parallel={})".format(rows, end - start, concurrent))

    return r


def test_load() -> RainbowTable:
    start = time.time()
    r = RainbowTable(iterations=iterations, reduction_fn=reduction_fn, hash_fn=hash_fn)
    r.load('test.csv')
    end = time.time()
    print("Finished filling {} rows in {:0.3f} seconds".format(rows, end - start))
    return r


def test_lookup(r: RainbowTable):
    plaintext = RainbowTable.get_random_plaintext(r)
    hash_str = hash_fn(plaintext)
    print(plaintext, hash_str)
    start = time.time()
    candidates = r.lookup(hash_str)
    end = time.time()
    print("Finished lookup in {:0.3f} seconds - found {} candidates".format(end - start, len(candidates)))


def test_fill_and_lookup(concurrent: bool, save: bool = True):
    r = test_fill(concurrent)
    if save:
        r.save('test.csv')
    test_lookup(r)


def test_load_and_lookup():
    r = test_load()
    test_lookup(r)


def convert_wordlist(input_filename: str, output_filename: str):
    open(output_filename, 'w').write('\n'.join(open(input_filename, 'r').readline().split(' ')))


if __name__ == '__main__':
    test_fill_and_lookup(True)
