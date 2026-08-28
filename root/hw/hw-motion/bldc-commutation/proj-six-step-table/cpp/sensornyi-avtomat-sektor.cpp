// Три ноги Голлів у молодших бітах: (HC<<2)|(HB<<1)|HA -> код 1..6.
// Значення 0 і 7 — несправність (обрив/КЗ датчика або шум).
// sector_of_hall[код] = номер сектора 0..5, або 0xFF як "недійсно".
static const uint8_t sector_of_hall[8] = {
    0xFF,  // 000 — недійсно
    0,     // 001 -> сектор 1
    2,     // 010 -> сектор 3
    1,     // 011 -> сектор 2
    4,     // 100 -> сектор 5
    5,     // 101 -> сектор 6
    3,     // 110 -> сектор 4
    0xFF,  // 111 — недійсно
};

static inline uint8_t read_hall_code(void) {
    // Прочитати три ноги портів; тут — умовні макроси читання піна.
    uint8_t a = gpio_read(HALL_A_PIN);
    uint8_t b = gpio_read(HALL_B_PIN);
    uint8_t c = gpio_read(HALL_C_PIN);
    return (uint8_t)((c << 2) | (b << 1) | a);
}

void commutate_from_hall(int forward) {
    uint8_t code = read_hall_code();
    uint8_t sector = sector_of_hall[code];
    if (sector == 0xFF) {
        drive_off();            // недійсний код -> знеструмити міст, не гадати
        fault_latch(FAULT_HALL);
        return;
    }
    uint8_t bits = step_bits(sector, forward);
    apply_inverter(bits);       // виставити ключі на цей сектор
}
