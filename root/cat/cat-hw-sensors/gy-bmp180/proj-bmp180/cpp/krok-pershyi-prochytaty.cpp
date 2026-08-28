#include <Wire.h>

static const uint8_t BMP180_ADDR = 0x77;   // адреса зашита намертво

// Прочитати 2 байти регістра `reg` як БЕЗЗНАКОВЕ 16-бітне (старший байт перший).
static uint16_t bmp180_read_u16(uint8_t reg) {
  Wire.beginTransmission(BMP180_ADDR);
  Wire.write(reg);
  Wire.endTransmission(false);          // повторний старт, шину не відпускаємо
  Wire.requestFrom((int)BMP180_ADDR, 2);
  uint8_t msb = Wire.read();
  uint8_t lsb = Wire.read();
  return ((uint16_t)msb << 8) | lsb;
}

// Те саме, але результат тлумачимо як ЗНАКОВЕ 16-бітне.
static int16_t bmp180_read_s16(uint8_t reg) {
  return (int16_t)bmp180_read_u16(reg);   // ті самі біти, інше тлумачення
}
