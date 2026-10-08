#include <Wire.h>

#define INA226_I2C_ADDR         0x40
#define INA226_REG_CONFIG       0x00
#define INA226_REG_MASK_ENABLE  0x06
#define INA226_REG_ALERT_LIMIT  0x07
#define ALERT_PIN               2

volatile bool alertTriggered = false;

void IRAM_ATTR alertISR() {
  alertTriggered = true;
}

void setupINA226Alert() {
  // Налаштовуємо усереднення 16 вибірок (CONFIG = 0x44B7)
  Wire.beginTransmission(INA226_I2C_ADDR);
  Wire.write(INA226_REG_CONFIG);
  Wire.write(0x44); Wire.write(0xB7);
  Wire.endTransmission();

  // Задаємо поріг перевантаження по струму 4.0 А (ALERT_LIMIT = 20000)
  Wire.beginTransmission(INA226_I2C_ADDR);
  Wire.write(INA226_REG_ALERT_LIMIT);
  Wire.write(0x4E); Wire.write(0x20);
  Wire.endTransmission();

  // Дозволяємо переривання по SOL та вмикаємо засувку Latch (0x8001)
  Wire.beginTransmission(INA226_I2C_ADDR);
  Wire.write(INA226_REG_MASK_ENABLE);
  Wire.write(0x80); Wire.write(0x01);
  Wire.endTransmission();
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  pinMode(ALERT_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ALERT_PIN), alertISR, FALLING);
  
  setupINA226Alert();
}

void loop() {
  if (alertTriggered) {
    alertTriggered = false;
    Serial.println("УВАГА: Перевищено поріг струму на шині!");

    // Скидаємо засувку ALERT шляхом читання регістра Mask/Enable
    Wire.beginTransmission(INA226_I2C_ADDR);
    Wire.write(INA226_REG_MASK_ENABLE);
    Wire.endTransmission(false);
    Wire.requestFrom((uint8_t)INA226_I2C_ADDR, (uint8_t)2);
    while(Wire.available()) Wire.read();
  }
}
