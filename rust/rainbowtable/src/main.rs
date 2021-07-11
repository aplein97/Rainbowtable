use std::fs::File;
use std::io::{BufRead, BufReader};

use std::process;
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

const RAINBOW_TABLE_PATH: &str = "./rainbow.table";
// Length of reduced passwords and hashes in characters (i.e. hash length is LENGTH*4 bits).
const LENGTH: usize = 8;
// Number of iterations for a rainbow table chain.
const ITERATIONS: u32 = 100;

const HASH_FUNC: HashFunc = |str| {
    let result = Sha3_224::digest(&str.as_bytes());
    return hex::encode(result)[0..LENGTH].to_string();
};

const REDUCTION_FUNC: ReductionFunc =
    |hash, index| reduction_function1(hash, LENGTH as u32, index);

fn _main_save() {
    let wordlist = match read_wordlist(RAINBOW_TABLE_PATH) {
        Ok(wordlist) => wordlist,
        Err(err) => panic!("{}", err),
    };
    let mut rt = RainbowTable::new(ITERATIONS, HASH_FUNC, REDUCTION_FUNC);
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

    if let Err(err) = rt.save_to_file("./rainbow.table") {
        println!("Failed to save rainbow table to file: {}", err);
        process::exit(1);
    }
}

fn main() {
    let mut rt = RainbowTable::new(ITERATIONS, HASH_FUNC, REDUCTION_FUNC);
    if let Err(err) = rt.load_from_file(RAINBOW_TABLE_PATH) {
        println!("Failed to load rainbow table from file: {}", err);
        process::exit(1);
    }

    println!("Loaded {} chains into rainbow table", rt.get_chain_count());
}
