// Функція опитування SCL із триточковим цифровим фільтром
static bool i2c_bb_read_scl_filtered(const i2c_bitbang_bus_t *bus) {
    uint8_t high_samples = 0;
    for (uint8_t i = 0; i < 3; i++) {
        if (bus->read_scl()) {
            high_samples++;
        }
    }
    // Рівень вважається високим, лише якщо щонайменше 2 вибірки з 3 підтвердили 1
    return (high_samples >= 2);
}
