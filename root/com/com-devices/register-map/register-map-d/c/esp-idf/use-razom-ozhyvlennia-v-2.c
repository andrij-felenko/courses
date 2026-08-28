// 1. Перевірка: чи це той чіп?
if (read_reg(REG_WHO) != EXPECTED_ID) {
    ESP_LOGE(TAG, "чіпа нема на 0x%02X — дроти або адреса", ADDR);
    vTaskDelete(NULL);                         // задачу далі не крутити
}

// 2. Налаштування (раз при старті задачі):
write_reg(REG_PWR, 0x00);                      // вийти зі сну
uint8_t c = read_reg(REG_CFG);                 // читай-зміни-запиши:
write_reg(REG_CFG, (c & ~0x18) | (0b10 << 3)); // діапазон AFS = ±8g

// 3. Читання виміру осі X (у циклі задачі FreeRTOS):
uint8_t hi = read_reg(REG_XOUT_H);
uint8_t lo = read_reg(REG_XOUT_H + 1);         // сусідня комірка 0x3C
int16_t raw = (int16_t)((hi << 8) | lo);       // склали два байти в число
float ax = raw / 4096.0f;                      // сирий відлік → g (±8g → 4096 LSB/g)
vTaskDelay(pdMS_TO_TICKS(10));                 // віддати процесор іншим задачам
