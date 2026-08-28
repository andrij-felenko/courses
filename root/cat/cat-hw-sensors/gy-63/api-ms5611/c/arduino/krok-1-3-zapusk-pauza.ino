// Обраний режим згладжування (код OSR: 0,2,4,6,8) і його пауза в мілісекундах.
static uint8_t g_osr_cmd = 8;        // 8 = OSR 4096 (найвища роздільність)

static uint16_t osr_delay_ms() {
  switch (g_osr_cmd) {
    case 0: return 1;   // ~0.6 мс, округляємо вгору
    case 2: return 2;   // ~1.2 мс
    case 4: return 3;   // ~2.3 мс
    case 6: return 5;   // ~4.6 мс
    default:return 10;  // ~9.1 мс (OSR 4096)
  }
}

// Запустити одне перетворення (start = CMD_CONV_D1 або CMD_CONV_D2),
// витримати паузу за OSR і прочитати 24-бітний результат АЦП.
static bool ms5611_convert_read(uint8_t start_cmd, uint32_t *out) {
  // -- запуск перетворення --
  Wire.beginTransmission(MS5611_ADDR);
  Wire.write(start_cmd + g_osr_cmd);       // напр. 0x40 + 8 = 0x48 для тиску @OSR4096
  if (Wire.endTransmission() != 0) return false;

  // -- пауза, поки АЦП рахує --
  delay(osr_delay_ms());

  // -- команда читання результату --
  Wire.beginTransmission(MS5611_ADDR);
  Wire.write(CMD_ADC_READ);                // 0x00
  if (Wire.endTransmission() != 0) return false;

  // -- забрати рівно 3 байти: 24 біти, старший першим --
  if (Wire.requestFrom((int)MS5611_ADDR, 3) != 3) return false;
  uint32_t b2 = Wire.read();               // старший
  uint32_t b1 = Wire.read();               // середній
  uint32_t b0 = Wire.read();               // молодший
  *out = (b2 << 16) | (b1 << 8) | b0;      // 24-бітне число

  // нульовий результат = давач не встиг/не відповів як слід
  return (*out != 0);
}
