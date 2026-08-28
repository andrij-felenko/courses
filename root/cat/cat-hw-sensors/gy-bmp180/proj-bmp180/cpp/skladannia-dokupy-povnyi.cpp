#include <Wire.h>
#include <math.h>

// ... сюди вставити всі функції вище:
// bmp180_read_u16/s16, bmp180_read_calibration,
// bmp180_read_ut/up, bmp180_compute_B5,
// bmp180_temperature, bmp180_pressure, bmp180_altitude ...

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 2000) { }

  // На ESP32/STM32/Pico задайте свої ніжки ДО решти:
  //   Wire.begin(21, 22);   // SDA=21, SCL=22 — типово для ESP32
  Wire.begin();

  if (!bmp180_read_calibration()) {
    Serial.println(F("BMP180 не відповідає або це не BMP180."));
    Serial.println(F("Перевірте живлення, землю й дроти SDA/SCL."));
    while (true) { delay(1000); }
  }
  Serial.println(F("BMP180 на зв'язку, калібрування прочитано."));
}

void loop() {
  float   t = bmp180_temperature();     // °C
  int32_t p = bmp180_pressure();        // Па
  float   h = bmp180_altitude(p);       // м над рівнем моря (стандартний p0)

  Serial.print(F("T = "));   Serial.print(t, 1);
  Serial.print(F(" C   P = ")); Serial.print(p / 100.0f, 2);   // → гПа
  Serial.print(F(" hPa   h = ")); Serial.print(h, 1);
  Serial.println(F(" m"));

  delay(1000);
}
