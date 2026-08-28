#include <Wire.h>
#include "MS5611.h"

// Конструктор приймає адресу; 0x77 — коли CSB вільний або на GND, 0x76 — коли CSB на VCC.
MS5611 baro(0x77);

float seaLevel_hPa = 1013.25;   // опорний тиск на рівні моря; уточнимо його нижче

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 2000) { }

  // На ESP32/STM32/Pico задайте ніжки шини ДО begin():
  Wire.begin(21, 22);            // SDA=21, SCL=22 — типово для ESP32
  // На класичній Arduino (UNO/Nano) ніжки жорсткі (A4/A5): просто Wire.begin();

  if (!baro.begin()) {
    Serial.println(F("MS5611 не відповідає. Перевірте дроти, адресу (0x76/0x77) і живлення."));
    while (true) { delay(1000); }
  }

  // Режим згладжування: від OSR_ULTRA_LOW (найшвидший, найгрубіший)
  // до OSR_ULTRA_HIGH (найдовша пауза ~9 мс, роздільність ~0.012 мбар — ті самі «10 см»).
  baro.setOversampling(OSR_ULTRA_HIGH);

  Serial.println(F("MS5611 на зв'язку."));
}

void loop() {
  int result = baro.read();      // повний вимір: D1, D2, обидва порядки компенсації
  if (result != MS5611_READ_OK) {
    Serial.print(F("read() error: "));
    Serial.println(result);
    delay(1000);
    return;
  }

  float t = baro.getTemperature();          // °C
  float p = baro.getPressure();             // мбар (гПа)
  float h = baro.getAltitude(seaLevel_hPa); // м над рівнем опорного тиску

  Serial.print(F("T = "));   Serial.print(t, 2);
  Serial.print(F(" °C   P = ")); Serial.print(p, 2);
  Serial.print(F(" hPa   h = ")); Serial.print(h, 1);
  Serial.println(F(" m"));

  delay(1000);
}
