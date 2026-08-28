// Час встановлення зовнішнього ЦАП (мкс) — залежить від мікросхеми
#define T_SETTLE_US  1
#define N_BITS       12

// Хелпери для конкретної схеми
// dac_write(): SPI-транзакція або dacWrite() на зовнішній 12-бітний ЦАП
static void dac_write(uint16_t code) {
    // Наприклад, MCP4922 через SPI:
    // spiTransfer(DAC_CS_PIN, (code >> 8) | 0x30, code & 0xFF);
    // Замініть на свій драйвер.
    (void)code;
}

// comparator_above(): читає GPIO компаратора.
// Полярність: повертає true, якщо Vtry > Vin (тобто «перебрали»).
// УВАГА: напрям залежить від підключення входів компаратора — перевірте схему!
static bool comparator_above(void) {
    return digitalRead(CMP_PIN) == HIGH;
}

// Ядро SAR: повертає 12-бітний код, що відповідає Vin
uint16_t sar_convert(void) {
    uint16_t code = 0;
    for (int b = N_BITS - 1; b >= 0; --b) {
        code |= (1u << b);             // пробуємо біт b = 1
        dac_write(code);               // виставити пробне Vtry на ЦАП
        delayMicroseconds(T_SETTLE_US);// ЧЕКАЄМО, поки ЦАП усталиться
        if (comparator_above()) {      // Vtry > Vin → перебрали
            code &= ~(1u << b);        // скинути біт — він зайвий
        }
        // якщо Vtry ≤ Vin → біт лишаємо
    }
    return code;
}
