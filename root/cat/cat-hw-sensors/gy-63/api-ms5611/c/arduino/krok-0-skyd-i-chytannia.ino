#include <Wire.h>

static const uint8_t MS5611_ADDR = 0x77;   // 0x76, якщо CSB на VCC

static const uint8_t CMD_RESET    = 0x1E;
static const uint8_t CMD_CONV_D1  = 0x40;   // тиск;  до цього додається OSR·2
static const uint8_t CMD_CONV_D2  = 0x50;   // темпер.; до цього додається OSR·2
static const uint8_t CMD_ADC_READ = 0x00;
static const uint8_t CMD_PROM_BASE= 0xA0;   // A0..AE — 8 слів по 16 біт

// Тут зберігатимемо весь PROM: [0]=reserved+CRC-nibble, [1..6]=C1..C6, [7]=serial+CRC.
uint16_t g_prom[8];

// Скид давача.
static bool ms5611_reset() {
  Wire.beginTransmission(MS5611_ADDR);
  Wire.write(CMD_RESET);
  bool ok = (Wire.endTransmission() == 0);
  delay(3);            // ~2.8 мс на перезавантаження PROM у регістри
  return ok;
}

// Прочитати одне 16-бітне слово PROM за індексом 0..7.
static bool ms5611_read_prom_word(uint8_t index, uint16_t *out) {
  Wire.beginTransmission(MS5611_ADDR);
  Wire.write(CMD_PROM_BASE + index * 2);      // A0, A2, A4, ... AE
  if (Wire.endTransmission() != 0) return false;

  if (Wire.requestFrom((int)MS5611_ADDR, 2) != 2) return false;
  uint8_t hi = Wire.read();
  uint8_t lo = Wire.read();
  *out = ((uint16_t)hi << 8) | lo;            // старший байт першим
  return true;
}

// Прочитати весь PROM (8 слів) у g_prom[]. Викликається раз при старті.
static bool ms5611_read_prom() {
  for (uint8_t i = 0; i < 8; i++) {
    if (!ms5611_read_prom_word(i, &g_prom[i])) return false;
  }
  return true;
}
