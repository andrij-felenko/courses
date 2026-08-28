#include <Wire.h>

void setup() {
  Wire.begin();               // старт шини I²C
  Serial.begin(115200);
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {   // 0 = пристрій відповів
      Serial.print("знайдено за адресою 0x");
      Serial.println(addr, HEX);
    }
  }
}

void loop() {}
