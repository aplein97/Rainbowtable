# Rainbow Table in Rust

## Usage

To build and run the application you need to [install Rust and Cargo](https://doc.rust-lang.org/cargo/getting-started/installation.html).

```
# Generate a rainbow table and store it in ./rainbow.table using the wordlist in ./wordlist.txt
$ cargo run --release -- --iterations=1000 --length=8 generate --wordlist=./wordlist.txt

# Perform a lookup:
$ cargo run --release -- --iterations=1000 --length=8 lookup --plaintext=yearlies
```

You can also first build and then run the binary directly:

```
$ cargo build --release
$ cd target/release
$ ./rainbowtable --iterations=1000 --length=8 generate --wordlist=./wordlist.txt
$ ./rainbowtable --iterations=1000 --length=8 lookup --plaintext=yearlies
```