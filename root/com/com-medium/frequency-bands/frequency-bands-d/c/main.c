// Довжина чвертьхвильової антени для частоти каналу.
// c у мм/с, щоб одразу дістати міліметри.
float quarter_wave_mm(float freq_hz) {
    const float c = 299792458.0f * 1000.0f;   // швидкість світла, мм/с
    float lambda_mm = c / freq_hz;            // λ = c / f
    return lambda_mm / 4.0f;                   // чверть хвилі
}

// 433 МГц → ≈173 мм (17 см);  2.4 ГГц → ≈31 мм (3 см)
float ant_433  = quarter_wave_mm(433.0e6f);
float ant_2400 = quarter_wave_mm(2400.0e6f);
