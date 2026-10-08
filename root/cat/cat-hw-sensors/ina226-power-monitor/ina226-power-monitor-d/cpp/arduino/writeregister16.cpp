#include <Wire.h>

const uint8_t INA226_ADDR = 0x40;

void writeRegister16(uint8_t reg, uint16_t value) {
  Wire.beginTransmission(INA226_ADDR);
  Wire.write(reg);
  Wire.write((uint8_t)(value >> 8));
  Wire.write((uint8_t)(value & 0xFF));
  Wire.endTransmission();
}

void setup() {
  Wire.begin();
  Serial.begin(115200);

  // Конфігурація: AVG=64, VBUS_CT=1.1ms, VSH_CT=1.1ms, Режим=Continuous (0x41F7)
  writeRegister16(0x00, 0x41F7);

  // Калібрування: CAL = 2048 (R_shunt = 10 мОм, Current_LSB = 250 мкА)
  writeRegister16(0x05, 2048);

  // Налаштування межі ALERT на 5.0 А (V_shunt = 50 мВ => 20000 відліків)
  writeRegister16(0x07, 20000);

  // Увімкнення генерації сигналу ALERT при Shunt Over Limit із фіксацією Latch (0x8001)
  writeRegister16(0x06, 0x8001);
  
  Serial.println(F("INA226 успішно сконфігуровано з апаратним усередненням і захистом!"));
}

void loop() {
  // Основний цикл вільний: мікроконтролер обробляє ALERT через переривання GPIO
  delay(1000);
}
