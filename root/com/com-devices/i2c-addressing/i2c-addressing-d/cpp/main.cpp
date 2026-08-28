#include <Wire.h>

void setup() {
  Wire.begin();
  Serial.begin(115200);

  for (uint8_t addr = 0x08; addr <= 0x77; addr++) {   // лише придатний діапазон
    Wire.beginTransmission(addr);        // старт + 7-бітна адреса + біт W
    if (Wire.endTransmission() == 0) {   // 0 == прийшов ACK на адресу
      Serial.print("found device at 0x");
      Serial.println(addr, HEX);         // друкуємо саме 7-бітну адресу
    }
  }
}

void loop() {}
