use std::fs::File;
use std::io::{BufRead, BufReader};

use std::process;
use std::time::Instant;

use clap::{App, Arg, SubCommand};

use sha3::{Digest, Sha3_224};

mod rainbow_table;
use rainbow_table::reduction::reduction_function1;
use rainbow_table::RainbowTable;

fn read_wordlist(path: &str) -> Result<Vec<String>, std::io::Error> {
    let file = File::open(path)?;
    let br = BufReader::new(file);
    br.lines().collect()
}

fn hash(plaintext: &str, length: u32) -> String {
    let result = Sha3_224::digest(&plaintext.as_bytes());
    return hex::encode(result)[0..(length as usize)].to_string();
}

fn generate_rainbowtable(
    iterations: u32,
    length: u32,
    rainbowtable_path: &str,
    wordlist_path: &str,
) {
    println!(
        "Generate rainbow table with iterations={}, reduced password length={}, reduced hash bit-length={}",
        iterations,
        length,
        length * 4
    );
    println!("Read from wordlist file {}", wordlist_path);
    println!("Save rainbow table into file {}", rainbowtable_path);
    println!("");

    let wordlist = match read_wordlist(wordlist_path) {
        Ok(wordlist) => wordlist,
        Err(err) => {
            println!("Failed to read wordlist: {}", err);
            process::exit(1);
        },
    };

    let mut rt = RainbowTable::new(
        iterations,
        Box::new(move |str: &str| hash(str, length)),
        Box::new(move |hash, index| reduction_function1(hash, length, index)),
    );
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

    if let Err(err) = rt.save_to_file(rainbowtable_path) {
        println!("Failed to save rainbow table to file: {}", err);
        process::exit(1);
    }
}

fn lookup_hash_of_plaintext(
    iterations: u32,
    length: u32,
    rainbowtable_path: &str,
    plaintext: &str,
) {
    println!(
        "Load rainbow table with iterations={}, reduced password length={}, reduced hash bit-length={} from file={}",
        iterations,
        length,
        length * 4,
        rainbowtable_path
    );

    let hash_length = length;
    let hash_func = Box::new(move |str: &str| hash(str, hash_length));
    let reduction_length = length;
    let mut rt = RainbowTable::new(
        iterations,
        hash_func,
        Box::new(move |hash, index| reduction_function1(hash, reduction_length, index)),
    );
    if let Err(err) = rt.load_from_file(rainbowtable_path) {
        println!("Failed to load rainbow table from file: {}", err);
        process::exit(1);
    }

    println!("Loaded {} chains into rainbow table", rt.get_chain_count());

    let hash = hash(plaintext, length);
    println!("Look for plaintext for hash {}", hash);

    let start = Instant::now();
    let result = rt.lookup(&hash);
    let elapsed = start.elapsed().as_secs_f64();

    match result {
        Some(candidate) => println!(
            "Found plaintext {} for hash {} in {}s",
            &candidate, &hash, elapsed
        ),
        None => println!("Found no plaintext for hash {} in {}s", &hash, elapsed),
    }
}

fn is_u32_arg(v: String) -> Result<(), String> {
    if v.parse::<u32>().is_ok() {
        return Ok(());
    }

    Err("The value is not a valid u32".into())
}

fn main() {
    let matches = App::new("RainbowTabler").version("0.1").author("Group 2")
        .arg(
            Arg::with_name("rainbowtable")
            .long("rainbowtable")
            .help("Sets the rainbowtable path. Either reads from or writes to, depending on command.")
            .takes_value(true)
            .default_value("./rainbow.table")
        )
        .arg(
            Arg::with_name("iterations")
            .long("iterations")
            .help("Sets the number of iterations used for generation and lookup.")
            .takes_value(true)
            .validator(is_u32_arg)
            .required(true)
        )
        .arg(
            Arg::with_name("length")
            .long("length")
            .help("The length of the reduced passwords and hashes. Hashes have length*4 bits.")
            .takes_value(true)
            .validator(is_u32_arg)
            .required(true)
        )
        .subcommand(
            SubCommand::with_name("generate")
            .about("Generates a rainbow table and saves it to file.")
            .arg(
                Arg::with_name("wordlist")
                .help("Path to the wordlist.")
                .takes_value(true)
                .long("wordlist")
                .required(true)
            )
        )
        .subcommand(
            SubCommand::with_name("lookup")
            .about("Looks up a hash that is generated from the given plaintext.")
            .arg(
                Arg::with_name("plaintext")
                .help("The plaintext whose hash has to be looked up in the rainbow table.")
                .takes_value(true)
                .long("plaintext")
                .required(true)
            )
        )
        .get_matches();

    let rainbowtable_path = matches.value_of("rainbowtable").unwrap();
    // The validator ensures that the value is an u32 so unwrap should be ok.
    let iterations: u32 = matches.value_of("iterations").unwrap().parse().unwrap();
    // The validator ensures that the value is an u32 so unwrap should be ok.
    let length: u32 = matches.value_of("length").unwrap().parse().unwrap();

    if let Some(matches) = matches.subcommand_matches("generate") {
        let wordlist_path = matches.value_of("wordlist").unwrap();
        generate_rainbowtable(iterations, length, rainbowtable_path, wordlist_path);
    } else if let Some(matches) = matches.subcommand_matches("lookup") {
        let plaintext = matches.value_of("plaintext").unwrap();
        lookup_hash_of_plaintext(iterations, length, rainbowtable_path, plaintext)
    }
}
