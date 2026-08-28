#include <Wire.h>
#include <Adafruit_BMP280.h>

Adafruit_BMP280 bmp(&Wire);   // об'єкт давача на шині I2C

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 2000) { }   // дочекатись термінала, але не вічно

  // На ESP32/Pico задайте свої ніжки шини ДО bmp.begin():
  //   Wire.begin(21, 22);        // SDA=21, SCL=22 — типово для ESP32
  //   Wire.begin(4, 5);          // SDA=GP4, SCL=GP5 — типово для Pico
  // На класичній Arduino (UNO/Nano) ніжки жорсткі (A4/A5) — Wire.begin() без аргументів.
  Wire.begin();

  // УВАГА: типова плата GY-BMP280 за замовчуванням сидить на 0x76,
  // а не на 0x77 (це «рідна» адреса Adafruit). Тому адресу задаємо явно.
  if (!bmp.begin(0x76)) {
    Serial.println(F("BMP280 не знайдено. Перевірте: 3.3 В, CSB вгору, адресу 0x76/0x77."));
    while (true) { delay(1000); }           // далі йти немає сенсу
  }
  Serial.println(F("BMP280 на зв'язку."));

  // Один раз налаштувати режим виміру: неперервний, обидва канали з
  // передискретизацією, помірний згладжувальний фільтр.
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,     // міряє сам, без запитів
                  Adafruit_BMP280::SAMPLING_X2,     // температура ×2
                  Adafruit_BMP280::SAMPLING_X16,    // тиск ×16 (найважливіше)
                  Adafruit_BMP280::FILTER_X16,      // сильний IIR-фільтр
                  Adafruit_BMP280::STANDBY_MS_500); // пауза 500 мс між вимірами
}

void loop() {
  float t = bmp.readTemperature();          // °C
  float p = bmp.readPressure();             // Па (не гПа!)
  float h = bmp.readAltitude(1013.25f);     // м, відносно стандартного рівня моря

  Serial.print(F("T = "));   Serial.print(t, 2);        Serial.print(F(" C   "));
  Serial.print(F("P = "));   Serial.print(p / 100.0f, 2); Serial.print(F(" hPa   "));
  Serial.print(F("h = "));   Serial.print(h, 1);        Serial.println(F(" m"));

  delay(1000);
}
