// Обраний режим згладжування (код OSR: 0,2,4,6,8) і його пауза в мілісекундах.
static uint8_t g_osr_cmd = 8;               // 8 = OSR 4096 (найвища роздільність)

// HAL_Delay(n) гарантує щонайменше n−1 мс, тому округляємо вгору з запасом.
static uint32_t osr_delay_ms(void) {
  switch (g_osr_cmd) {
    case 0:  return 2;    // ~0.6 мс
    case 2:  return 3;    // ~1.2 мс
    case 4:  return 4;    // ~2.3 мс
    case 6:  return 6;    // ~4.6 мс
    default: return 11;   // ~9.1 мс (OSR 4096)
  }
}

// Запустити одне перетворення (start_cmd = CMD_CONV_D1 або CMD_CONV_D2),
// витримати паузу за OSR і прочитати 24-бітний результат АЦП.
static bool ms5611_convert_read(uint8_t start_cmd, uint32_t *out) {
  uint8_t cmd = start_cmd + g_osr_cmd;      // напр. 0x40 + 8 = 0x48 для тиску @OSR4096
  if (HAL_I2C_Master_Transmit(&hi2c1, MS5611_ADDR, &cmd, 1, I2C_TMO) != HAL_OK) return false;

  HAL_Delay(osr_delay_ms());                // пауза, поки АЦП рахує

  cmd = CMD_ADC_READ;                       // 0x00
  if (HAL_I2C_Master_Transmit(&hi2c1, MS5611_ADDR, &cmd, 1, I2C_TMO) != HAL_OK) return false;

  uint8_t buf[3];
  if (HAL_I2C_Master_Receive(&hi2c1, MS5611_ADDR, buf, 3, I2C_TMO) != HAL_OK) return false;

  // 24 біти, старший байт першим
  *out = ((uint32_t)buf[0] << 16) | ((uint32_t)buf[1] << 8) | buf[2];

  // нульовий результат = давач не встиг/не відповів як слід
  return (*out != 0);
}
