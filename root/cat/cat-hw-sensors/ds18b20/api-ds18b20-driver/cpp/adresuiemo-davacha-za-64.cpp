#include <OneWire.h>
#include <DallasTemperature.h>

OneWire oneWire(4);
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(115200);
  sensors.begin();

  uint8_t n = sensors.getDeviceCount();     // скільки давачів знайшлось
  Serial.print("Знайдено давачів: ");
  Serial.println(n);

  DeviceAddress addr;                        // це просто uint8_t[8]
  for (uint8_t i = 0; i < n; i++) {
    if (sensors.getAddress(addr, i)) {       // забрати код i-го давача
      Serial.print("Давач ");
      Serial.print(i);
      Serial.print(": { ");
      for (uint8_t b = 0; b < 8; b++) {
        Serial.print("0x");
        if (addr[b] < 16) Serial.print('0'); // провідний нуль для рівних чисел
        Serial.print(addr[b], HEX);
        if (b < 7) Serial.print(", ");
      }
      Serial.println(" }");                  // готово вставляти в код
    }
  }
}

void loop() {}
