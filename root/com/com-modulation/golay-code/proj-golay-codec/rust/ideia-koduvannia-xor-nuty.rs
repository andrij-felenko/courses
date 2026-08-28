/// Рядки симетричної матриці B (кожен u16 — 12-бітний рядок:
/// біт j дорівнює елементу B[i][j]).
const B: [u16; 12] = [
    0xA3B, 0xD1D, 0xE8E, 0xB47, 0xDA3, 0xED1,
    0xF68, 0xBB4, 0x9DA, 0x8ED, 0xC76, 0x7FF,
];

/// m·B над GF(2): XOR рядків B, де в m стоїть одиниця.
fn times_b(m: u16) -> u16 {
    let mut acc = 0u16;
    for i in 0..12 {
        if m & (1u16 << i) != 0 { acc ^= B[i]; }
    }
    acc
}

/// Кодування: 12 бітів даних -> [дані(12) | перевірка(12)] в u32.
pub fn encode(data: u16) -> u32 {
    let data = data & 0x0FFF;
    data as u32 | (times_b(data) as u32) << 12
}
