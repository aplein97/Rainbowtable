import unittest
import reduction


class TestReductionFunction1(unittest.TestCase):
    def test_success(self):
        hash = '3c62c99bafbe3a81f16d36b592b66ae5'
        expected = 'bbfaeens'
        self.assertEqual(reduction.reduction_function1(hash, 8, 6), expected)

    def test_invalid_hash(self):
        with self.assertRaises(ValueError):
            reduction.reduction_function1('', 1, 0)

    def test_invalid_length(self):
        with self.assertRaises(ValueError):
            reduction.reduction_function1('abc', 0, 0)

    def test_invalid_index(self):
        with self.assertRaises(ValueError):
            reduction.reduction_function1('abc', 1, -1)


if __name__ == '__main__':
    unittest.main()
