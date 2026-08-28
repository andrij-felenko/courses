// Точний коефіцієнт інвертувального каскаду зі скінченним підсиленням A.
// r1, r2 — опори (Ом); a_ol — підсилення без зворотного зв'язку (рази).
// Повертає Uвих/Uвх (від'ємний). При a_ol → ∞ прямує до −r2/r1.
float inverting_gain_finite(float r1, float r2, float a_ol)
{
    float ideal = r2 / r1;                 // ідеальне |підсилення|
    float noise_gain = 1.0f + r2 / r1;     // шумовий коефіцієнт (1 + R2/R1)
    return -ideal / (1.0f + noise_gain / a_ol);
}
// inverting_gain_finite(1000, 99000, 1e4f) -> -98.02 (а не -99)
