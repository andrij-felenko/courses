// Ініціалізація та блокування параметрів ISP сенсора OV2640
void camera_sensor_lock_isp_configuration(void) {
    // 1. Перехід у банк регістрів DSP (0xFF -> 0x00)
    sccb_write_reg(0xFF, 0x00);

    // 2. Вимкнення автоматичного балансу білого (AWB) для усунення колірного дрейфу
    // Регістр 0xC7 (COM8): біт 1 скидаємо в 0 (Disable AWB)
    uint8_t com8 = sccb_read_reg(0xC7);
    sccb_write_reg(0xC7, com8 & ~0x02);

    // 3. Встановлення фіксованого підсилення червоного та синього каналів (D65 сонячне світло)
    sccb_write_reg(0xCC, 0x5E); // Red Gain Manual = 1.47x
    sccb_write_reg(0xCD, 0x48); // Blue Gain Manual = 1.12x

    // 4. Фіксація порогу максимального автопідсилення (AGC Ceiling)
    // Регістр 0x03 (COM9): встановлюємо стелю підсилення 4x замість 32x для зниження шуму
    uint8_t com9 = sccb_read_reg(0x03);
    sccb_write_reg(0x03, (com9 & 0x8F) | 0x10);

    // 5. Увімкнення апаратної корекції віньєтування лінзи (Lens Shading Correction)
    sccb_write_reg(0xFF, 0x01); // Банк регістрів Sensor
    uint8_t com7 = sccb_read_reg(0x12);
    sccb_write_reg(0x12, com7 | 0x20); // Enable LSC
}
