# this class describes the data structure behind the rainbow table
# usage:
# r = RainbowTable()  # creates a rainbow table
# r.load('../test.csv')  # loads rainbow table from file

class RainbowTable:

    def __init__(self):
        # TODO: add hash-function and reduction-function as arguments/attributes and use them in methods below
        self.table = dict()

    def has(self, hash_text: str) -> bool:
        """
        check if the rainbow table has the given hash in the most right column
        :param hash_text: the hash to search for
        :return: True, if the hash is found, otherwise False
        """
        return hash_text in self.table

    def lookup(self, hash_text: str) -> str:
        """
        get the first column of a row where the given hash is in the last column
        :param hash_text: the hash to search for in the last column
        :return: the plaintext value from the first column
        """
        return self.table.get(hash_text)

    def get_plain(self, hash_str: str) -> str or None:
        # TODO: implement method
        """
        gets the plaintext of a given hash
        :param hash_str: the hash to search for
        :return: the plaintext (if the hash was found) or None
        """
        # should search for a hash (if not found, return None)
        # if found, get plaintext of that row and calculate complete row, find plaintext for hash
        # -> need hash-function and reduction-function for this!
        return None

    def put(self, hash_text: str, plain_text: str):
        """
        save a first column / last column pair of a row in the rainbow table
        :param hash_text: last columns value of the row in the rainbow table
        :param plain_text: the forst columns value of the row in the rainbow table
        """
        self.table[hash_text] = plain_text

    def save(self, filename: str):
        """
        save the current dictionary as CSV file
        :param filename: where to store the file
        """
        # TODO: save as CSV
        pass

    def load(self, filename: str):
        """
        load a dictionary from a CSV file into this rainbow table object
        :param filename: the filename of the CSV file
        """
        # TODO: populate table from CSV
        pass
