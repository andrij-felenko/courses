// Ініціалізація та блокування параметрів ISP сенсора через об'єктний I2C контролер
void camera_sensor_lock_isp_configuration(I2cInterface& bus) {
    // 1. Перехід у банк регістрів DSP (0xFF -> 0x00)
    bus.write_reg(0xFF, 0x00);

    // 2. Вимкнення автоматичного балансу білого (AWB)
    const uint8_t com8 = bus.read_reg(0xC7);
    bus.write_reg(0xC7, static_cast<uint8_t>(com8 & ~0x02));

    // 3. Встановлення фіксованого підсилення кольору
    bus.write_reg(0xCC, 0x5E); // Red Gain Manual = 1.47x
    bus.write_reg(0xCD, 0x48); // Blue Gain Manual = 1.12x

    // 4. Фіксація стелі автопідсилення AGC на рівні 4x
    const uint8_t com9 = bus.read_reg(0x03);
    bus.write_reg(0x03, static_cast<uint8_t>((com9 & 0x8F) | 0x10));

    // 5. Увімкнення корекції віньєтування (Lens Shading)
    bus.write_reg(0xFF, 0x01);
    const uint8_t com7 = bus.read_reg(0x12);
    bus.write_reg(0x12, static_cast<uint8_t>(com7 | 0x20));
}
