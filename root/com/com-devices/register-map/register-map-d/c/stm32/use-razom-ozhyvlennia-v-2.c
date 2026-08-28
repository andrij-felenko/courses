// 1. Перевірка: чи це той чіп?
if (read_reg(REG_WHO) != EXPECTED_ID) {
    Error_Handler();                           // біда з дротами або адресою
}

// 2. Налаштування (раз при старті, після MX_I2C1_Init()):
write_reg(REG_PWR, 0x00);                      // вийти зі сну
uint8_t c = read_reg(REG_CFG);                 // читай-зміни-запиши:
write_reg(REG_CFG, (c & ~0x18) | (0b10 << 3)); // діапазон AFS = ±8g

// 3. Читання виміру осі X (у головному циклі):
uint8_t hi = read_reg(REG_XOUT_H);
uint8_t lo = read_reg(REG_XOUT_H + 1);         // сусідня комірка 0x3C
int16_t raw = (int16_t)((hi << 8) | lo);       // склали два байти в число
float ax = raw / 4096.0f;                      // сирий відлік → g (±8g → 4096 LSB/g)
HAL_Delay(10);
