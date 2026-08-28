// ESP32, I²C вже ініціалізовано. Адреса FT6206-класу — 0x38.
#define TS_ADDR     0x38
#define REG_NUM     0x02   // кількість активних точок
#define REG_P1_XH   0x03   // далі XH, XL, YH, YL для точки 1

uint8_t buf[5];
i2c_read(TS_ADDR, REG_NUM, buf, 5);    // читаємо лічильник + 4 байти точки

uint8_t touches = buf[0] & 0x0F;        // молодші 4 біти — кількість дотиків
if (touches > 0) {
    // XH: біти 7..6 — прапорець події, біти 3..0 — старші біти X
    uint16_t x = ((buf[1] & 0x0F) << 8) | buf[2];
    uint16_t y = ((buf[3] & 0x0F) << 8) | buf[4];
    // тепер (x, y) — сирі координати контролера
}
