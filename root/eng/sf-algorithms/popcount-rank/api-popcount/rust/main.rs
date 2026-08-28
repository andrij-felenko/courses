// Сигнатури базових методів
pub const fn count_ones(self) -> u32;
pub const fn count_zeros(self) -> u32;
pub const fn leading_zeros(self) -> u32;
pub const fn trailing_zeros(self) -> u32;

// Приклад використання в середовищі no_std
let mask: u64 = 0b1011_0000_1111;
let weight: u32 = mask.count_ones(); // Повертає 8
let parity: bool = (weight % 2) != 0;
