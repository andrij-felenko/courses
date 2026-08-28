static const uint8_t REG_READ  = 0xE7;   // читати регістр налаштувань 1
static const uint8_t REG_WRITE = 0xE6;   // писати регістр налаштувань 1
static const uint8_t HEATER_BIT = 0x04;  // біт 2 = вмикання нагрівача (HTRE)

// Прочитати регістр налаштувань 1. Повертає true й кладе байт у *reg_out.
static bool gy21_read_user_reg(uint8_t *reg_out) {
  Wire.beginTransmission(GY21_ADDR);
  Wire.write(REG_READ);
  if (Wire.endTransmission() != 0) return false;
  if (Wire.requestFrom((int)GY21_ADDR, 1) != 1) return false;
  *reg_out = Wire.read();
  return true;
}

// Увімкнути (on=true) чи вимкнути (on=false) вбудований нагрівач —
// НЕ чіпаючи бітів роздільності (read-modify-write).
bool gy21_set_heater(bool on) {
  uint8_t reg;
  if (!gy21_read_user_reg(&reg)) return false;   // 1) прочитати поточний стан

  if (on) reg |=  HEATER_BIT;                      // 2) виставити або
  else    reg &= ~HEATER_BIT;                      //    скинути лише біт 2

  Wire.beginTransmission(GY21_ADDR);               // 3) записати назад
  Wire.write(REG_WRITE);
  Wire.write(reg);
  return (Wire.endTransmission() == 0);
}
