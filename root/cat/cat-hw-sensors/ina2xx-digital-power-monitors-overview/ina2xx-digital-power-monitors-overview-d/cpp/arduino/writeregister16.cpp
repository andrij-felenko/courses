#include <Wire.h>

#define INA226_I2C_ADDR         0x40
#define INA226_REG_CALIBRATION  0x05
#define INA226_REG_CURRENT      0x04
#define INA226_REG_POWER        0x03

const float CURRENT_LSB = 0.0002f; // 200 мкА/LSB
const float POWER_LSB = 0.005f;   // 5 мВт/LSB

void writeRegister16(uint8_t reg, uint16_t value) {
  Wire.beginTransmission(INA226_I2C_ADDR);
  Wire.write(reg);
  Wire.write((uint8_t)(value >> 8));
  Wire.write((uint8_t)(value & 0xFF));
  Wire.endTransmission();
}

int16_t readRegister16(uint8_t reg) {
  Wire.beginTransmission(INA226_I2C_ADDR);
  Wire.write(reg);
  Wire.endTransmission(false);
  Wire.requestFrom((uint8_t)INA226_I2C_ADDR, (uint8_t)2);
  if (Wire.available() >= 2) {
    return (int16_t)((Wire.read() << 8) | Wire.read());
  }
  return 0;
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  
  // Конфігуруємо регістр калібрування
  writeRegister16(INA226_REG_CALIBRATION, 2560);
}

void loop() {
  int16_t rawCurrent = readRegister16(INA226_REG_CURRENT);
  uint16_t rawPower = (uint16_t)readRegister16(INA226_REG_POWER);

  float currentAmps = rawCurrent * CURRENT_LSB;
  float powerWatts = rawPower * POWER_LSB;

  Serial.print("Струм: "); Serial.print(currentAmps, 3); Serial.println(" A");
  Serial.print("Потужність: "); Serial.print(powerWatts, 3); Serial.println(" Вт");

  delay(1000);
}
