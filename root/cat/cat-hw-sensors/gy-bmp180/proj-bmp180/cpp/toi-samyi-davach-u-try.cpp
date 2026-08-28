#include <Wire.h>
#include <Adafruit_BMP085.h>

Adafruit_BMP085 bmp;

void setup() {
  Serial.begin(115200);
  Wire.begin();                       // на ESP32 — Wire.begin(21, 22);
  if (!bmp.begin()) {                 // читає 0x55, тягне всі 11 коефіцієнтів
    Serial.println(F("BMP180 не знайдено."));
    while (true) { delay(1000); }
  }
}

void loop() {
  Serial.print(F("T = "));   Serial.print(bmp.readTemperature());   // °C, float
  Serial.print(F(" C   P = ")); Serial.print(bmp.readPressure());   // Па, int32
  Serial.print(F(" Pa   h = ")); Serial.print(bmp.readAltitude());  // м
  Serial.println(F(" m"));
  delay(1000);
}
