use std::cmp::Ordering;

// Одна пара ідентифікаторів передвипуску: правила 11.4.1–11.4.3 специфікації.
fn cmp_id(a: &str, b: &str) -> Ordering {
    let num = |s: &str| s.bytes().all(|c| c.is_ascii_digit());
    match (num(a), num(b)) {
        // обидва числові: без провідних нулів довший = більший, за рівної довжини — лексично.
        (true, true)   => a.len().cmp(&b.len()).then_with(|| a.cmp(b)),
        (true, false)  => Ordering::Less,     // числовий ЗАВЖДИ нижчий за буквений
        (false, true)  => Ordering::Greater,
        (false, false) => a.cmp(b),           // обидва буквені — лексично, в ASCII-порядку
    }
}

// Передвипуски двох версій з РІВНИМ ядром: правила 11.2 і 11.4.
fn cmp_prerelease(a: &[&str], b: &[&str]) -> Ordering {
    match (a.is_empty(), b.is_empty()) {
        (true, true)   => Ordering::Equal,     // обидва готові — рівні
        (true, false)  => Ordering::Greater,   // готовий випуск старший за передвипуск
        (false, true)  => Ordering::Less,
        (false, false) => a.iter().copied().zip(b.iter().copied())
            .map(|(x, y)| cmp_id(x, y))
            .find(|o| o.is_ne())               // перша ж відмінність вирішує все
            .unwrap_or_else(|| a.len().cmp(&b.len())),  // рівний префікс → довший набір старший
    }
}
