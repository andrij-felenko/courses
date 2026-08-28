#include <Wire.h>

static const uint8_t BMP280_ADDR = 0x76;   // типова адреса GY-BMP280 (SDO донизу)

// Прочитати ОДИН байт із регістра reg. Повертає true й кладе значення в *out.
static bool rd8(uint8_t reg, uint8_t *out) {
  Wire.beginTransmission(BMP280_ADDR);
  Wire.write(reg);
  if (Wire.endTransmission() != 0) return false;   // давач не підтвердив адресу
  if (Wire.requestFrom((int)BMP280_ADDR, 1) != 1) return false;
  *out = Wire.read();
  return true;
}

// Прочитати `len` байтів ПОСПІЛЬ, починаючи з регістра reg, у буфер buf.
// BMP280 сам збільшує внутрішній лічильник адреси, тож блок читається одним заходом.
static bool rdN(uint8_t reg, uint8_t *buf, uint8_t len) {
  Wire.beginTransmission(BMP280_ADDR);
  Wire.write(reg);
  if (Wire.endTransmission() != 0) return false;
  if (Wire.requestFrom((int)BMP280_ADDR, (int)len) != len) return false;
  for (uint8_t i = 0; i < len; i++) buf[i] = Wire.read();
  return true;
}

// Записати ОДИН байт val у регістр reg. Повертає true при ACK.
static bool wr8(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(BMP280_ADDR);
  Wire.write(reg);
  Wire.write(val);
  return (Wire.endTransmission() == 0);
}
