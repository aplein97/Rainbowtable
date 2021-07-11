use std::fs::File;
use std::io::{BufRead, BufReader};

use std::time::Instant;

use sha3::{Digest, Sha3_224};

mod rainbow_table;
use rainbow_table::reduction::reduction_function1;
use rainbow_table::RainbowTable;

use crate::rainbow_table::{HashFunc, ReductionFunc};

fn read_wordlist(path: &str) -> Result<Vec<String>, std::io::Error> {
    let file = File::open(path)?;
    let br = BufReader::new(file);
    br.lines().collect()
}

fn main() {
    // Length of reduced passwords and hashes in characters (i.e. hash length is LENGTH*4 bits).
    const LENGTH: usize = 8;
    // Number of iterations for a rainbow table chain.
    const ITERATIONS: u32 = 100;

    let hash_func: HashFunc = |str| {
        let result = Sha3_224::digest(&str.as_bytes());
        return hex::encode(result)[0..LENGTH].to_string();
    };

    let reduction_func: ReductionFunc =
        |hash, index| reduction_function1(hash, LENGTH as u32, index);

    let wordlist = match read_wordlist("./wordlist.txt") {
        Ok(wordlist) => wordlist,
        Err(err) => panic!("{}", err),
    };
    let mut rt = RainbowTable::new(ITERATIONS, hash_func, reduction_func);
    let start = Instant::now();
    if let Err(err) = rt.fill_parallel(&wordlist) {
        panic!("{}", err);
    }

    let elapsed = start.elapsed().as_secs_f64();
    println!(
        "{} chains from {} words in {} seconds",
        rt.get_chain_count(),
        wordlist.len(),
        elapsed,
    );
}
