#include <Wire.h>

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 2000) { }   // дочекатись термінала, але не вічно

  // На ESP32/STM32/Pico тут ЗАДАЙТЕ свої ніжки, напр. Wire.begin(21, 22);
  // На класичній Arduino (UNO/Nano) пін жорсткий (A4/A5) — просто Wire.begin();
  Wire.begin();

  Serial.println(F("\nСканую шину I2C..."));
}

void loop() {
  uint8_t found = 0;

  for (uint8_t addr = 0x08; addr <= 0x77; addr++) {   // валідні 7-бітні адреси
    Wire.beginTransmission(addr);
    uint8_t err = Wire.endTransmission();             // 0 = ACK, пристрій є

    if (err == 0) {
      Serial.printf("  знайдено пристрій за 0x%02X", addr);
      // підкажемо, схоже це на дисплей чи ні:
      if (addr >= 0x20 && addr <= 0x27) Serial.print(F("  (схоже на PCF8574 — I2C-LCD)"));
      if (addr >= 0x38 && addr <= 0x3F) Serial.print(F("  (схоже на PCF8574A — I2C-LCD)"));
      Serial.println();
      found++;
    }
  }

  if (found == 0)
    Serial.println(F("  нічого. Перевір живлення, дроти SDA/SCL і підтяжки."));
  else
    Serial.printf("Разом пристроїв: %u\n", found);

  delay(3000);   // повторюємо кожні 3 с, щоб бачити, як щось зникає/з'являється
}
