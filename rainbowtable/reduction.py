def reduction_function1(hash, length, index):
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
