#define BMP_ID      0xD0     // паспорт, віддає 0x58
#define BMP_RESET   0xE0
#define BMP_CTRL    0xF4     // керування вимірами (oversampling + режим)
#define BMP_CONFIG  0xF5
#define BMP_PRESS   0xF7     // 0xF7..0xF9 тиск, 0xFA..0xFC температура
#define BMP_CALIB   0x88     // 24 байти калібрування (12 коефіцієнтів)

int bmp280_init(void) {
    if (read_u8(BMP_ADDR, BMP_ID) != 0x58) return 0;   // не BMP280
    i2c_write_reg(BMP_ADDR, BMP_RESET, 0xB6);          // м'який скид
    delay_ms(10);
    // Читаємо 24 байти калібрування у структуру (порядок — little-endian):
    uint8_t cal[24];
    i2c_read_regs(BMP_ADDR, BMP_CALIB, cal, 24);
    bmp280_store_calib(cal);                           // розкласти по dig_T*/dig_P*
    // Oversampling ×16 по тиску й ×2 по температурі, безперервний режим:
    i2c_write_reg(BMP_ADDR, BMP_CTRL, 0x57);
    i2c_write_reg(BMP_ADDR, BMP_CONFIG, 0x10);         // фільтр IIR
    delay_ms(10);
    return 1;
}
