// значення полінома на наборі x: ⊕ коефіцієнтів усіх підмножин x
fn anf_eval(coef: &[u8], x: usize) -> u8 {
    let (mut acc, mut m) = (0u8, x);
    loop {
        acc ^= coef[m];
        if m == 0 { break; }
        m = (m - 1) & x;              // наступна підмножина маски x
    }
    acc
}

// алгебричний степінь; -1 для тотожного нуля
fn anf_degree(coef: &[u8]) -> i32 {
    coef.iter().enumerate()
        .filter(|&(_, &c)| c != 0)
        .map(|(m, _)| m.count_ones() as i32)
        .max()
        .unwrap_or(-1)
}

// лінійна (афінна) ⟺ жодного доданка з двох і більше змінних
fn is_affine(coef: &[u8]) -> bool {
    coef.iter().enumerate()
        .all(|(m, &c)| c == 0 || m.count_ones() < 2)
}
