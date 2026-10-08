#include <Wire.h>

const uint8_t INA226_ALERT_PIN = 2;
const uint8_t POWER_MOSFET_PIN = 3;
const uint8_t INA226_I2C_ADDR = 0x40;
const uint8_t INA226_REG_MASK_ENABLE = 0x06;

volatile bool alertFlag = false;

// Неблокувальний обробник переривання (ISR)
void IRAM_ATTR handleInaAlert() {
  digitalWrite(POWER_MOSFET_PIN, LOW); // Апаратний захист: негайно вимикаємо ключ
  alertFlag = true;                    // Фіксуємо прапорець для циклу loop()
}

uint16_t readRegister16(uint8_t reg) {
  Wire.beginTransmission(INA226_I2C_ADDR);
  Wire.write(reg);
  Wire.endTransmission(false);
  Wire.requestFrom(INA226_I2C_ADDR, (uint8_t)2);
  if (Wire.available() >= 2) {
    uint16_t value = Wire.read() << 8;
    value |= Wire.read();
    return value;
  }
  return 0;
}

void setup() {
  pinMode(POWER_MOSFET_PIN, OUTPUT);
  digitalWrite(POWER_MOSFET_PIN, HIGH); // Подача живлення

  pinMode(INA226_ALERT_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(INA226_ALERT_PIN), handleInaAlert, FALLING);

  Wire.begin();
  Serial.begin(115200);
}

void loop() {
  if (alertFlag) {
    // Зчитування регістру 0x06 для скидання засувки LATCH та визначення прапорця
    uint16_t maskValue = readRegister16(INA226_REG_MASK_ENABLE);
    Serial.print(F("ALERT ISR executed! Mask/Enable reg = 0x"));
    Serial.println(maskValue, HEX);
    
    alertFlag = false;
  }
}
