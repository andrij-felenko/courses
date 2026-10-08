#include <Wire.h>

const uint8_t BMP280_ADDR = 0x76;

bool initSensorReset() {
  Wire.beginTransmission(BMP280_ADDR);
  Wire.write(0xD0); // Регістр ID
  if (Wire.endTransmission() != 0) return false;
  
  Wire.requestFrom(BMP280_ADDR, (uint8_t)1);
  uint8_t chipId = Wire.read();
  if (chipId != 0x58 && chipId != 0x60) return false;
  
  // Виконання програмного скидання
  Wire.beginTransmission(BMP280_ADDR);
  Wire.write(0xE0); // Регістр reset
  Wire.write(0xB6); // Команда скидання
  Wire.endTransmission();
  
  // Перевірка прапорця im_update у регістрі status (0xF3)
  uint8_t status = 0;
  do {
    Wire.beginTransmission(BMP280_ADDR);
    Wire.write(0xF3);
    Wire.endTransmission();
    Wire.requestFrom(BMP280_ADDR, (uint8_t)1);
    status = Wire.read();
  } while (status & 0x01);
  
  return true;
}
