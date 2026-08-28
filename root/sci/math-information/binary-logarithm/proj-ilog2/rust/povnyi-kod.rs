// B(2,6), укладена так, що вгорі стоїть її вікно з шести нулів.
// Стала не єдина можлива: таких є 2²⁶ · 2. Ця — найменша лексикографічно.
const DEBRUIJN: u64 = 0x0218_a392_cd3d_5dbf;

// Таблицю будує компілятор ще до запуску — тим самим виразом, що й гарячий код.
const fn make_table() -> [u8; 64] {
    let mut t = [0u8; 64];
    let mut k = 0;
    while k < 64 {
        let hash = ((1u64 << k).wrapping_mul(DEBRUIJN) >> 58) as usize;
        t[hash] = k as u8;
        k += 1;
    }
    t
}
const TAB: [u8; 64] = make_table();

/// ⌊log₂n⌋ для n > 0. На нулі НЕ визначено — див. «Пастки».
fn floor_log2_debruijn(mut n: u64) -> u32 {
    n |= n >> 1;   n |= n >> 2;    n |= n >> 4;    // розмазали старший біт донизу:
    n |= n >> 8;   n |= n >> 16;   n |= n >> 32;   // n стало 2ᵏ⁺¹ − 1
    let msb = n - (n >> 1);                        // лишили сам старший біт: 2ᵏ
    TAB[(msb.wrapping_mul(DEBRUIJN) >> 58) as usize] as u32
}
