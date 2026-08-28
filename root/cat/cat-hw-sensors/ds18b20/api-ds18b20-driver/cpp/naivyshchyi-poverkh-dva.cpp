#include <OneWire.h>
#include <DallasTemperature.h>

const uint8_t PIN_1WIRE = 4;          // лінія DQ шини 1-Wire
OneWire oneWire(PIN_1WIRE);
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(115200);
  sensors.begin();                    // знайти давачі, зчитати їхні коди
}

void loop() {
  sensors.requestTemperatures();      // АКТ: скидання→Skip ROM→Convert T усім
  float t = sensors.getTempCByIndex(0);  // АКТ: скидання→Read Scratchpad, декод

  if (t == DEVICE_DISCONNECTED_C) {   // -127.0: не відповів або CRC не зійшлось
    Serial.println("DS18B20 не на звязку");
  } else {
    Serial.print(t, 4);               // уже в °C
    Serial.println(" C");
  }
  delay(1000);
}
