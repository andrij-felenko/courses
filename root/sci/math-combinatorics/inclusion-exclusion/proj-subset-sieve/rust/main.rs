fn coprime_count(n: i64, primes: &[i64]) -> i64 {
    let r = primes.len();
    let mut total: i64 = 0;
    for mask in 0u32..(1 << r) {
        let mut prod: i64 = 1;
        let mut over = false;
        for (i, &pi) in primes.iter().enumerate() {
            if (mask >> i) & 1 == 1 {
                // checked_mul повертає None при переповненні i64 — мова ловить пастку сама
                match prod.checked_mul(pi) {
                    Some(v) if v <= n => prod = v,
                    _ => { over = true; break; }    // переповнення АБО добуток > N → доданок 0
                }
            }
        }
        let term = if over { 0 } else { n / prod };            // ⌊N / добуток⌋
        total += if mask.count_ones() & 1 == 1 { -term } else { term };  // знак за парністю
    }
    total
}

fn divisible_by_any(n: i64, primes: &[i64]) -> i64 {
    n - coprime_count(n, primes)
}
