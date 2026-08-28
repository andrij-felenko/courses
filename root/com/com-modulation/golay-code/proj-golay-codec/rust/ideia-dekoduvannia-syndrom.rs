/// Синдром s = B·x ⊕ y. Для симетричної B  B·x = x·B.
fn syndrome(r: u32) -> u16 {
    let x = (r & 0x0FFF) as u16;
    let y = ((r >> 12) & 0x0FFF) as u16;
    times_b(x) ^ y
}

/// Патерн помилки (24 біти) — або None, якщо помилок 4+.
pub fn error_pattern(r: u32) -> Option<u32> {
    let s = syndrome(r);
    if s.count_ones() <= 3 {
        return Some((s as u32) << 12);
    }
    for i in 0..12 {
        let t = s ^ B[i];
        if t.count_ones() <= 2 {
            return Some((1u32 << i) | (t as u32) << 12);
        }
    }
    let s2 = times_b(s);                       // B·s, бо B² = I
    if s2.count_ones() <= 3 {
        return Some(s2 as u32);
    }
    for i in 0..12 {
        let t = s2 ^ B[i];
        if t.count_ones() <= 2 {
            return Some((1u32 << (i + 12)) | t as u32);
        }
    }
    None
}

/// Виправлені 12 бітів даних — або None, якщо слово невиправне.
pub fn decode(r: u32) -> Option<u16> {
    error_pattern(r).map(|e| ((r ^ e) & 0x0FFF) as u16)
}
