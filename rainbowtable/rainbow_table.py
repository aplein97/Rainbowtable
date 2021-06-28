import csv
import multiprocessing
import os
import random
from typing import Callable, Dict, List


# this class describes the data structure behind the rainbow table
# usage:
# r = RainbowTable()  # creates a rainbow table
# r.load('../test.csv')  # loads rainbow table from file


class RainbowTable:

    def __init__(self, iterations: int, reduction_fn: Callable[[str, int], str], hash_fn: Callable[[str], str]):
        self._data: Dict[str, List[str]] = dict()

        # rainbow table settings
        self._iterations = iterations
        self._reduction_fn = reduction_fn
        self._hash_fn = hash_fn

    def _has(self, key: str) -> bool:
        """
        check if the rainbow table has the given key in the most right column
        :param key: the key to search for
        :return: True, if at least one value is found, otherwise False
        """
        return key in self._data and len(self._data[key]) > 0

    def _get(self, key: str) -> List[str]:
        """
        get the first column of a row where the given key is in the last column
        :param key: the key to search for in the last column
        :return: the values from the first column (may be empty)
        """
        return self._data.get(key) or []

    def _put(self, key: str, value: str):
        """
        save a first column / last column pair of a row in the rainbow table
        :param key: last columns value of the row in the rainbow table
        :param value: the first columns value of the row in the rainbow table
        """
        if key not in self._data:
            self._data.update({key: [value]})
        elif value not in self._data[key]:
            self._data.update({key: [*self._data[key], value]})

    def _calculate_row(self, initial_str: str) -> str:
        """
        calculate a row from an initial plaintext and return last column
        :param initial_str: the initial plaintext where the calculation starts
        :return: the last column
        """
        key = initial_str

        for i in range(1, self._iterations):
            hash_str = self._hash_fn(key)
            key = self._reduction_fn(hash_str, i)

        return key

    def clear(self):
        """
        clears the data structure, emptying the rainbow table
        """
        self._data.clear()

    def save(self, filename: str):
        """
        save the current dictionary as CSV file
        :param filename: where to store the file
        """

        try:
            with open(filename, 'w') as csv_file:
                writer = csv.writer(csv_file)
                for key, values in self._data.items():
                    for value in values:
                        writer.writerow([value, key])
        except IOError:
            print("I/O error")

    def load(self, filename: str):
        """
        load a dictionary from a CSV file into this rainbow table object
        :param filename: the filename of the CSV file
        """

        try:
            with open(filename, 'r') as csv_file:
                self._data.clear()

                reader = csv.reader(csv_file)
                for item in reader:
                    self._put(item[1], item[0])
        except IOError:
            print("I/O error")

    def get_random_plaintext(self):
        choices = [item for sublist in self._data.values() for item in sublist]

        value = random.choice(choices)

        for i in range(1, random.randint(0, self._iterations - 1)):
            hash_str = self._hash_fn(value)
            value = self._reduction_fn(hash_str, i)

        return value

    def lookup(self, hash_str: str) -> List[str]:
        """
        looks up the plaintext of a given hash
        :param hash_str: the hash to search for
        :return: List of possible plaintext candidates (may be empty)
        """

        candidates = []

        # iterate through columns
        for i in range(self._iterations - 1, 0, -1):
            candidates += self._lookup_for_iteration(hash_str, i)

        return candidates

    def _lookup_for_iteration(self, hash_str: str, iteration: int) -> List[str]:
        """
        try to lookup the row containing the given hash
        this method assumes that the reduction of the given hash is the column of the given iteration
        """
        candidates = []
        tmp_hash_str = hash_str

        for i in range(iteration, self._iterations):
            tmp = self._reduction_fn(tmp_hash_str, i)

            # iterate through all found rows
            for value in self._get(tmp):

                # calculate reductions until correct column
                for j in range(1, iteration):
                    value = self._reduction_fn(self._hash_fn(value), j)

                # verify match and add it to candidates list
                if hash_str == self._hash_fn(value) and value not in candidates:
                    candidates.append(value)

            # get new hash from reduction
            tmp_hash_str = self._hash_fn(tmp)

        return candidates

    def fill(self, rows: int, generator_fn: Callable[[], str], concurrent: bool = False):
        """
        generates and calculates rows (of given count), using the given password candidate generator fn
        :param rows: the count of rows to generate
        :param generator_fn: a function which generates password candidates
        :param concurrent: whether to use multiprocessing
        """

        if concurrent:
            self._fill_multiprocessing(rows, generator_fn)
        else:
            self._fill(rows, generator_fn)

    def _fill_multiprocessing(self, rows: int, generator_fn: Callable[[], str]):
        """
        generates and calculates rows (of given count), using the given password candidate generator fn
        this method uses multiprocessing
        :param rows: the count of rows to generate
        :param generator_fn: a function which generates password candidates
        """

        with multiprocessing.Pool(processes=os.cpu_count()) as pool:
            words = [generator_fn() for _ in range(0, rows)]
            results = pool.map(self._calculate_row, words)
            pool.close()
            pool.join()

            for i in range(0, rows):
                self._put(results[i], words[i])

    def _fill(self, rows: int, generator_fn: Callable[[], str]):
        """
        generates and calculates rows (of given count), using the given password candidate generator fn
        this method doesn't use multiprocessing
        :param rows: the count of rows to generate
        :param generator_fn: a function which generates password candidates
        """

        for _ in range(0, rows):
            word = generator_fn()
            result = self._calculate_row(word)
            self._put(result, word)
