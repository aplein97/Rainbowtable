import random
import string
import sys


def reduction_function1(hash_str: str, length: int, index: int) -> str:
    """
    A function to reduce a given hash to a plaintext password of the given length.

    Based on https://link.springer.com/chapter/10.1007/978-3-642-30436-1_42
    """
    if length < 1:
        raise ValueError('length must be greater 0')
    if index < 0:
        raise ValueError('index must be greater or equal 0')

    # Convert hash from string into int
    number = int(''.join(map(str, map(ord, hash))))
    number = (number + index) % 26**length
    result = ''
    for _ in range(0, length):
        result += chr((number % 26) + ord('a'))
        number = number // 26

    return result


def reduction_function2(hash_str: str, length: int, index: int) -> str:
    """
    A function to reduce a given hash to a plaintext password of the given length.

    Based on https://link.springer.com/chapter/10.1007/978-3-642-30436-1_42
    """
    if length < 1:
        raise ValueError('length must be greater 0')
    if index < 0:
        raise ValueError('index must be greater or equal 0')

    if len(hash_str) % 2 == 1:
        hash_str += random.choice(string.digits + 'abcdef')

    # Convert hash from string into int
    number = int.from_bytes(bytes.fromhex(hash_str), byteorder='big', signed=False)
    # number = (number + index) % 26**length
    number = number % 26**length
    result = ''
    for _ in range(0, length):
        result += chr((number % 26) + ord('a'))
        number = number // 26

    return result


def reduction_function3(hash_str: str, length: int, index: int) -> str:
    if len(hash_str) % 2 == 1:
        hash_str += random.choice(string.digits + 'abcdef')

    hash_bytes = bytes.fromhex(hash_str)
    i = int.from_bytes(hash_bytes, byteorder=sys.byteorder)

    result_string = ""
    alphabet = string.ascii_lowercase
    base = len(alphabet)
    while i:
        i, idx = divmod(i, base)
        result_string = alphabet[idx:idx+1] + result_string
    return result_string[:length]
