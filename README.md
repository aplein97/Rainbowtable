# Rainbowtable

In this repository you will find a [Python implementation](python) and a
[Rust port](rust/rainbowtable) of that tool for generating rainbow tables and lookup of. For some
details please have a look at the Wiki but especially at the [presentations](presentations).

While the Python implementation's `run.py` has to be adjusted for the task you want to perform, the
Rust application offers a CLI for playing around.

## Generated Rainbow Tables

Both, the Python and the Rust implementation, accept the same format for

- **wordlist**: Text file with one word each line, no trailling whitespaces
- **rainbow.table**: The generated rainbow table, a CSV-file containing the first and last column
  of each chain

In [generated-tables](generated-tables) you will find an generated rainbow table with the
corresponding input word list. That rainbow table was created with the following attributes:

- *Iterations:* 10000
- *Length:* 8 (= 4*8 bits and reduced password length of 8)
