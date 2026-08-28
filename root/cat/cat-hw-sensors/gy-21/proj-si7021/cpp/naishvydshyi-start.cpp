#include <Wire.h>
#include <Adafruit_Si7021.h>

Adafruit_Si7021 sensor;   // об'єкт давача

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 2000) { }   // дочекатись термінала, але не вічно

  // На ESP32/STM32/Pico задайте свої ніжки шини ДО begin():
  //   Wire.begin(21, 22);        // SDA=21, SCL=22 — типово для ESP32
  // На класичній Arduino (UNO/Nano) ніжки жорсткі (A4/A5) — Wire.begin() без аргументів.
  Wire.begin();

  if (!sensor.begin()) {
    Serial.println(F("GY-21 не відповідає. Перевірте живлення й дроти SDA/SCL."));
    while (true) { delay(1000); }           // далі йти немає сенсу
  }
  Serial.println(F("GY-21 на зв'язку."));
}

void loop() {
  float t  = sensor.readTemperature();   // °C
  float rh = sensor.readHumidity();      // %

  Serial.print(F("T = "));
  Serial.print(t, 2);
  Serial.print(F(" °C   RH = "));
  Serial.print(rh, 1);
  Serial.println(F(" %"));

  delay(2000);        // раз на 2 с — щоб давач не грів сам себе (див. пастки)
}
