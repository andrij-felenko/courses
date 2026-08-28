// 1. Перевірка: чи це той чіп?
if (readReg(REG_WHO) != EXPECTED_ID) {
    // біда з дротами або адресою — далі не йти
    return;
}

// 2. Налаштування (раз при старті):
writeReg(REG_PWR, 0x00);                       // вийти зі сну
uint8_t c = readReg(REG_CFG);                  // читай-зміни-запиши:
writeReg(REG_CFG, (c & ~0x18) | (0b10 << 3));  // діапазон AFS = ±8g

// 3. Читання виміру осі X (у головному циклі):
uint8_t hi = readReg(REG_XOUT_H);
uint8_t lo = readReg(REG_XOUT_H + 1);          // сусідня комірка 0x3C
int16_t raw = (int16_t)((hi << 8) | lo);       // склали два байти в число
float ax = raw / 4096.0f;                       // сирий відлік → g (±8g → 4096 LSB/g)
