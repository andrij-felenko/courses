#define QMC_ADDR    0x0D
#define QMC_DATA    0x00   // X(L,H) Y(L,H) Z(L,H) — LSB першим
#define QMC_STATUS  0x06   // біт 0 = DRDY (дані готові), біт 1 = OVL (переповнення)
#define QMC_CONFIG1 0x09
#define QMC_RESET   0x0B

// ±2 Гаус → 12000 LSb/Gauss; ±8 Гаус → 3000 LSb/Gauss (datasheet QST)
#define QMC_LSB_PER_GAUSS 12000.0f

void qmc_init(void) {
    i2c_write_reg(QMC_ADDR, 0x0A, 0x80);   // м'яке скидання
    // (у власному HAL тут коротка пауза ~5 мс)
    i2c_write_reg(QMC_ADDR, QMC_RESET, 0x01);          // SET/RESET Period — ОБОВ'ЯЗКОВО
    i2c_write_reg(QMC_ADDR, QMC_CONFIG1, 0x1D);        // 512x, ±2G, 200Гц, безперервний
}

bool qmc_read_raw(int16_t *x, int16_t *y, int16_t *z) {
    uint8_t st;
    if (i2c_read_regs(QMC_ADDR, QMC_STATUS, &st, 1) != 0) return false;
    if (!(st & 0x01)) return false;        // DRDY=0 → нових даних ще немає
    uint8_t b[6];
    if (i2c_read_regs(QMC_ADDR, QMC_DATA, b, 6) != 0) return false;
    // little-endian: молодший байт першим
    *x = (int16_t)((b[1] << 8) | b[0]);
    *y = (int16_t)((b[3] << 8) | b[2]);
    *z = (int16_t)((b[5] << 8) | b[4]);
    if (st & 0x02) return false;           // OVL=1 → переповнення діапазону
    return true;
}
