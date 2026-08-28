/// Момент інерції однорідного диска (вісь ⟂ через центр) — сітка n×n.
/// Контроль: має збігтися з 0.5·M·R².
fn disc_inertia_grid(r_disc: f64, m: f64, n: usize) -> f64 {
    let step = 2.0 * r_disc / n as f64;       // сторона клітинки
    let mut s = 0.0;                          // Σ r²
    let mut inside = 0u64;
    for i in 0..n {
        let x = -r_disc + (i as f64 + 0.5) * step;
        for j in 0..n {
            let y = -r_disc + (j as f64 + 0.5) * step;
            let r2 = x * x + y * y;
            if r2 <= r_disc * r_disc {         // клітинка всередині диска?
                s += r2;
                inside += 1;
            }
        }
    }
    s * (m / inside as f64)                     // J = Σ r²·Δm
}
