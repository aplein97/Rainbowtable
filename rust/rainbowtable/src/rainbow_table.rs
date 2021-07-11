pub mod reduction;

use rayon::prelude::*;
use reduction::ReductionError;
use std::collections::HashMap;

pub type HashFunc = fn(&str) -> String;

pub type ReductionFunc = fn(&str, u32) -> Result<String, ReductionError>;

pub struct RainbowTable {
    /// Each chain will be calculated using the reduction function R_i with R_1..R_(iterations - 1)
    iterations: u32,
    /// Maps each plaintext from the *last column* to its corresponding plaintext in the first column.
    table: HashMap<String, String>,
    /// The hash function to use for chain generation and lookup.
    hash_func: HashFunc,
    /// The reduction function to use for chain generation and lookup.
    reduction_func: ReductionFunc,
}

impl RainbowTable {
    pub fn new(
        iterations: u32,
        hash_func: HashFunc,
        reduction_func: ReductionFunc,
    ) -> RainbowTable {
        RainbowTable {
            table: HashMap::new(),
            iterations,
            hash_func,
            reduction_func,
        }
    }

    /// Generates a chain for each word in the given wordlist and stores it into the rainbow table.
    pub fn fill(&mut self, wordlist: &[String]) -> Result<(), ReductionError> {
        for word in wordlist {
            let last_column = self.calc_chain(word)?;
            self.table.insert(last_column, word.to_string());
        }

        Ok(())
    }

    /// Generates a chain for each word in the given wordlist in parallel and stores it into the
    /// rainbow table.
    pub fn fill_parallel(&mut self, wordlist: &[String]) -> Result<(), ReductionError> {
        let result = wordlist
            .par_iter()
            .map(|word| self.calc_chain(word).map(|res| (word, res)))
            .collect::<Result<Vec<(&String, String)>, _>>()?;

        self.table.extend(
            result
                .into_iter()
                .map(|(word, last_column)| (last_column, word.clone())),
        );

        Ok(())
    }

    /// Loads a rainbow table from a CSV file into this instance.
    pub fn load_from_file(&mut self, path: &str) -> Result<(), csv::Error> {
      let mut rdr = csv::ReaderBuilder::new()
        .has_headers(false)
        .from_path(path)?;

      self.table.clear();
      for result in rdr.records() {
          let record = result?;
          self.table.insert(String::from(&record[1]), String::from(&record[0]));
      }

      Ok(())
    }

    /// Saves the current rainbow table as a CSV file at the given path.
    pub fn save_to_file(&self, path: &str) -> Result<(), csv::Error> {
        let mut wtr = csv::Writer::from_path(path)?;
        for (last_column, first_column) in self.table.iter() {
            wtr.write_record(&csv::StringRecord::from(vec![first_column, last_column]))?
        }

        wtr.flush()?;
        Ok(())
    }

    pub fn get_chain_count(&self) -> usize {
        return self.table.len();
    }

    /// Generates a single chain starting with the given word and returns the value of the last
    /// column.
    fn calc_chain(&self, word: &str) -> Result<String, ReductionError> {
        let mut last_column = word.to_string();
        for i in 1..(self.iterations) {
            let hash = (self.hash_func)(&last_column);
            last_column = match (self.reduction_func)(&hash, i) {
                Ok(next_plaintext) => next_plaintext,
                Err(err) => return Err(err),
            };
        }

        return Ok(last_column.to_string());
    }
}
