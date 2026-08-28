// SMBus Read Word: код 0x09 → два байти LSB-перший
uint8_t  cmd = 0x09;            // Voltage()
uint8_t  raw[2];               // [0]=молодший, [1]=старший
smbus_read_word(BATT_ADDR7, cmd, raw);   // BATT_ADDR7 == 0x0B

uint16_t mv = (uint16_t)raw[0] | ((uint16_t)raw[1] << 8);
// raw = {0x24, 0x1F} → mv = 0x24 | (0x1F << 8) = 0x1F24 = 7972

float volts = mv / 1000.0f;    // одиниця регістра — мілівольти
// volts ≈ 7.97 В  → двобанковий Li-ion пакет
