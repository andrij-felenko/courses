#include <Wire.h>

#define SDA_PIN 8
#define SCL_PIN 9

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 2000) {}

  // Явно кажемо, які ноги — SDA і SCL, і на якій швидкості (100 кГц — стандарт).
  Wire.begin(SDA_PIN, SCL_PIN, 100000);
  Serial.println("Сканую шину I2C...");
}

void loop() {
  int found = 0;
  for (uint8_t addr = 0x08; addr <= 0x77; addr++) {
    Wire.beginTransmission(addr);         // готуємо звертання до adr
    uint8_t err = Wire.endTransmission(); // 0, якщо хтось відповів ACK
    if (err == 0) {
      Serial.printf("  знайдено пристрій за адресою 0x%02X\n", addr);
      found++;
    }
  }
  if (found == 0)
    Serial.println("  нікого. Перевір підтяжки, живлення й виводи.");
  Serial.println("---");
  delay(3000);
}
