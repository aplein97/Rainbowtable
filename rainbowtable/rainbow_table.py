import csv
import multiprocessing
import os
import random
import threading
from typing import Callable, Dict, List


# this class describes the data structure behind the rainbow table
# usage:
# r = RainbowTable()  # creates a rainbow table
# r.load('../test.csv')  # loads rainbow table from file


class RainbowTable:

    def __init__(self, iterations: int, reduction_fn: Callable[[str], str], hash_fn: Callable[[str], str], concurrency: bool = False):
        self._concurrency = concurrency

        self._data: Dict[str, List[str]] = dict()
        self._lock = threading.Lock()

        # rainbow table settings
        self._iterations = iterations
        self._reduction_fn = reduction_fn
        self._hash_fn = hash_fn

    def _init_concurrency(self, m: multiprocessing.Manager):
        assert self._concurrency is True

        # initialize dict using the multiprocessing manager
        self._data: Dict[str, List[str]] = m.dict(self._data)
        self._lock = m.Lock()

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

        with self._lock:
            if key not in self._data:
                self._data.update({key: [value]})
            elif value not in self._data[key]:
                self._data.update({key: [*self._data[key], value]})

    def _calculate_row(self, initial_str: str, iterations: int) -> str:
        """
        calculate a row from an initial plaintext and return last column
        :param initial_str: the initial plaintext where the calculation starts
        :return: the last column
        """
        key = initial_str

        for i in range(0, iterations):
            hash_str = self._hash_fn(key)
            key = self._reduction_fn(hash_str)

        return key

    def clear(self):
        """
        clears the data structure, emptying the rainbow table
        """
        with self._lock:
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

        with self._lock:
            try:
                with open(filename, 'r') as csv_file:
                    self._data.clear()

                    reader = csv.reader(csv_file)
                    for item in reader:
                        self._put(item[1], item[0])
            except IOError:
                print("I/O error")

    def add_row(self, initial_str: str):
        """
        Calculates and adds a row based on the initial plaintext
        :param initial_str: the initial plaintext where the calculation starts
        :param m: a multiprocessing manager
        """
        last_column = self._calculate_row(initial_str, self._iterations)
        self._put(last_column, initial_str)

    def get_random_plaintext(self):
        with self._lock:
            choices = [item for sublist in self._data.values() for item in sublist]

        value = random.choice(choices)

        for i in range(0, random.randint(0, self._iterations)):
            hash_str = self._hash_fn(value)
            value = self._reduction_fn(hash_str)

        return value

    def lookup(self, hash_str: str) -> List[str]:
        """
        looks up the plaintext of a given hash
        :param hash_str: the hash to search for
        :return: List of possible plaintext candidates (may be empty)
        """

        candidates = []

        tmp_hash_str = hash_str

        # iterate through columns
        for i in range(self._iterations - 1, -1, -1):
            # reduce hash
            tmp = self._reduction_fn(tmp_hash_str)

            # iterate through all found rows
            for value in self._get(tmp):

                # calculate reductions until correct column
                for j in range(0, i):
                    value = self._reduction_fn(self._hash_fn(value))

                # verify match and add it to candidates list
                if hash_str == self._hash_fn(value) and value not in candidates:
                    candidates.append(value)

            # get new hash from reduction
            tmp_hash_str = self._hash_fn(tmp)

        return candidates

    def fill(self, rows: int, generator_fn: Callable[[], str]):
        if self._concurrency:
            cpu_count = os.cpu_count() or 1
            m = multiprocessing.Manager()
            self._init_concurrency(m)
            pool = multiprocessing.Pool()
            pool.apply(self._fill, (rows % cpu_count, generator_fn))
            pool.starmap(self._fill, [(rows // cpu_count, generator_fn) for _ in range(0, cpu_count)])
            pool.close()
            pool.join()
        else:
            self._fill(rows, generator_fn)

    def _fill(self, rows: int, generator_fn: Callable[[], str]):
        for _ in range(0, rows):
            self.add_row(generator_fn())
