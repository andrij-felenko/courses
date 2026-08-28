#include <OneWire.h>
#include <DallasTemperature.h>

const uint8_t PIN_1WIRE = 4;        // спільна лінія DQ шини 1-Wire
OneWire oneWire(PIN_1WIRE);
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(9600);
  sensors.begin();                  // знайти давачі на шині
}

void loop() {
  sensors.requestTemperatures();    // команда «виміряти» всім давачам
  float t = sensors.getTempCByIndex(0);   // забрати число з першого

  if (t == DEVICE_DISCONNECTED_C) { // -127: давач не відповів
    Serial.println("DS18B20 не на звязку");
  } else {
    Serial.print(t, 2);             // уже в °C, дві цифри після коми
    Serial.println(" C");
  }
  delay(1000);
}
