// Сходинки прискореного заряду: поки SOC нижчий за поріг — тримаємо струм цієї сходинки.
// Струми в мА для комірки 3000 мА·год: 1.5C → 1.0C → 0.6C → 0.3C.
struct Step { uint8_t soc_hi; uint16_t i_ma; };
static constexpr Step STEPS[] = {
    { 30, 4500 },   // 0..30%  — порожньо, межа висока: 1.5C
    { 60, 3000 },   // 30..60% — 1.0C
    { 80, 1800 },   // 60..80% — 0.6C
    {100,  900 },   // 80..100% — хвіст: 0.3C, далі перехід у CV
};

uint16_t boost_charge_setpoint(uint8_t soc, float cell_temp_c) {
    // Поза температурним вікном швидкий заряд заборонено — тут жодних сходинок.
    if (cell_temp_c < 10.0f || cell_temp_c > 45.0f) return 0;
    for (const Step& s : STEPS)
        if (soc < s.soc_hi)
            return s.i_ma;             // струм поточної сходинки
    return 0;                          // повна — заряд зупинено
}
