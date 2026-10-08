#include <Wire.h>

// I2C адреса та регістри давача BME280
static const uint8_t BME280_I2C_ADDR    = 0x76;
static const uint8_t REG_CTRL_HUM        = 0xF2;
static const uint8_t REG_CTRL_MEAS       = 0xF4;
static const uint8_t REG_CONFIG          = 0xF5;

void setupBME280DigitalPipeline() {
  Wire.begin();

  // 1. Конфігурація оверсемплінгу вологості (ctrl_hum = 0xF2)
  // osrs_h = x1 (біти [2:0] = 0b001)
  // Запис у ctrl_hum набуває чинності лише після наступного запису в ctrl_meas
  Wire.beginTransmission(BME280_I2C_ADDR);
  Wire.write(REG_CTRL_HUM);
  Wire.write(0x01);
  Wire.endTransmission();

  // 2. Конфігурація IIR-фільтра та періоду Standby (config = 0xF5)
  // t_sb = 1000 мс (біти [7:5] = 0b101), filter = x4 (біти [4:2] = 0b010), spi3w_en = 0
  // Результат: (0b101 << 5) | (0b010 << 2) = 0xA0 | 0x08 = 0xA8
  Wire.beginTransmission(BME280_I2C_ADDR);
  Wire.write(REG_CONFIG);
  Wire.write(0xA8);
  Wire.endTransmission();

  // 3. Конфігурація оверсемплінгу T, P та режиму Normal mode (ctrl_meas = 0xF4)
  // osrs_t = x2 (біти [7:5] = 0b010), osrs_p = x16 (біти [4:2] = 0b101), mode = Normal (біти [1:0] = 0b11)
  // Результат: (0b010 << 5) | (0b101 << 2) | 0b11 = 0x40 | 0x14 | 0x03 = 0x57
  Wire.beginTransmission(BME280_I2C_ADDR);
  Wire.write(REG_CTRL_MEAS);
  Wire.write(0x57);
  Wire.endTransmission();
}
