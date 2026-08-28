// Женемо `table` з чистої стрічки, не більш як `cap` кроків.
// Повертає (зупинилась?, кроків, одиниць).
fn simulate(table: &[u32], n: u32, cap: u64) -> (bool, u64, u64) {
    let width = (2 * cap + 3) as usize;
    let mut tape = vec![0u8; width];       // стрічка — щільний масив
    let mut h = (cap + 1) as usize;        // голівка стартує в центрі
    let mut st = 0u32;                     // стан A
    let mut steps = 0u64;
    loop {
        let sym = tape[h];
        let a = table[(st * 2 + sym as u32) as usize];
        tape[h] = write(a);
        steps += 1;
        if target(a) == n {                // перейшли в стан зупинки
            let ones = tape.iter().map(|&b| b as u64).sum();
            return (true, steps, ones);
        }
        h = (h as i64 + dir(a)) as usize;  // зсув на одну клітинку
        st = target(a);
        if steps >= cap {                  // СТЕЛЯ — далі не женемо
            let ones = tape.iter().map(|&b| b as u64).sum();
            return (false, steps, ones);
        }
    }
}
