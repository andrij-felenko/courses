// Cargo.toml: [dependencies] statrs = "0.16"

use statrs::function::gamma::digamma;

const EULER_MASCHERONI: f64 = 0.57721566490153286060_f64;

pub fn harmonic_eval(x: f64) -> Result<f64, &'static str> {
    if x < 0.0 {
        return Err("Аргумент x повинен бути >= 0");
    }
    if x == 0.0 {
        return Ok(0.0);
    }
    
    // H[x] = digamma(x + 1) + gamma
    let dig = digamma(x + 1.0);
    Ok(dig + EULER_MASCHERONI)
}

fn main() {
    match harmonic_eval(10.0) {
        Ok(val) => println!("H[10] = {:.15}", val),
        Err(e) => eprintln!("Помилка: {}", e),
    }
}
