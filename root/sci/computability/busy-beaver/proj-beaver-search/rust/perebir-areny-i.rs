fn hunt(n: u32, cap: u64) -> (u64, u64, u64, u64, u64) {
    let a_size = 4 * n + 4;                 // дій на клітинку
    let cells = (2 * n) as usize;
    let mut table = vec![0u32; cells];
    table[0] = 7;                           // старт-нормалізація: A,0 = (1,R,B) = 7
    let free = cells - 1;                    // вільні клітинки — 1 … cells-1
    let mut idx = vec![0u32; free];          // мішано-основний лічильник
    let (mut total, mut halted, mut undecided) = (0u64, 0u64, 0u64);
    let (mut best_ones, mut best_steps) = (0u64, 0u64);
    loop {
        for i in 0..free { table[i + 1] = idx[i]; }
        total += 1;
        let (ok, steps, ones) = simulate(&table, n, cap);
        if ok {
            halted += 1;
            best_ones = best_ones.max(ones);      // рекорд одиниць  → Σ(n)
            best_steps = best_steps.max(steps);   // рекорд кроків   → S(n)
        } else {
            undecided += 1;                       // ще працює на стелі
        }
        // ++лічильник за основою a_size; переповнення → арену пройдено
        let mut k = 0;
        while k < free { idx[k] += 1; if idx[k] < a_size { break; } idx[k] = 0; k += 1; }
        if k == free { break; }
    }
    (total, halted, undecided, best_ones, best_steps)
}
