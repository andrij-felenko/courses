#include <Wire.h>

void setup() {
  Serial.begin(115200);
  while (!Serial) { }            // на ESP32/native USB — дочекатися монітора
  Wire.begin();                  // SDA=GPIO21, SCL=GPIO22 на ESP32 за замовчуванням
  Serial.println("Скануємо шину I2C...");

  int found = 0;
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    uint8_t err = Wire.endTransmission();   // 0 == дістали ACK, пристрій живий
    if (err == 0) {
      Serial.printf("  пристрій за адресою 0x%02X\n", addr);
      found++;
    }
  }
  if (found == 0)
    Serial.println("Ніхто не озвався — перевір дроти, живлення, підтяжки.");
}

void loop() { }
