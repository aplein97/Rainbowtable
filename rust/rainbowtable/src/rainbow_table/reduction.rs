use std::ops::Add;

use custom_error::custom_error;
use num::bigint::ParseBigIntError;
use num::{BigUint, FromPrimitive, Integer, ToPrimitive};

custom_error! {pub ReductionError
  Format{source: ParseBigIntError} = "some input is of invalid format",
  Other{message: String} = "{message}"
}

/// A function to reduce a given hash to a plaintext password of the given length.
///
/// Based on https://link.springer.com/chapter/10.1007/978-3-642-30436-1_42
pub fn reduction_function1(
    hash_str: &str,
    length: u32,
    index: u32,
) -> Result<String, ReductionError> {
    // number = int(''.join(map(str, map(ord, hash_str))))

    // Generate an iterator where each value is the unicode point of each char in the hash string.
    let step_n_3 = hash_str.chars().map(|c| c as u8);
    // Convert each of the unicode points into a string.
    let step_n_2 = step_n_3.map(|byte| byte.to_string());
    // Join them together to a single string.
    let step_n_1 = step_n_2.collect::<Vec<String>>().join("");
    // Parse the string as the big int it might be.
    let step_n = step_n_1.parse::<BigUint>()?;

    // number = (number + index) % 26 ** length
    let num_26 = match BigUint::from_i32(26) {
        Some(n) => n,
        // This shouldn't possibly happen.
        None => {
            return Err(ReductionError::Other {
                message: "26 into bigint failed".into(),
            })
        }
    };
    let mut number = step_n + index % num_26.pow(length);

    // result = ''
    // for _ in range(0, length):
    //     result += chr((number % 26) + ord('a'))
    //     number = number // 26
    let mut result = String::new();
    for _ in 0..length {
        let (quotient, remainder) = number.div_rem(&num_26);
        // ord('a') == 97
        let codepoint = match (remainder + 97u32).to_u32() {
            Some(u) => u,
            None => {
                return Err(ReductionError::Other {
                    message: "codepoint error".into(),
                })
            }
        };
        let char = match char::from_u32(codepoint) {
            Some(char) => char,
            None => {
                return Err(ReductionError::Other {
                    message: "char from codepoint failed".into(),
                })
            }
        };
        result = result.add(&char.to_string());
        number = quotient;
    }

    return Ok(result);
}
