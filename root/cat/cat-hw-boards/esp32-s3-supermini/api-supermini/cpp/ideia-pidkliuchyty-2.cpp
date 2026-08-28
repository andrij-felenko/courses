#include <Wire.h>
#include <Adafruit_BMP280.h>

#define SDA_PIN 8
#define SCL_PIN 9
#define BMP_ADDR 0x76

Adafruit_BMP280 bmp;   // працює через глобальний Wire

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 2000) {}
  Wire.begin(SDA_PIN, SCL_PIN, 100000);

  // begin сам прочитає ідентифікатор і поверне false, якщо чипа немає
  // або адреса не та — тому перевіряти результат обов'язково.
  if (!bmp.begin(BMP_ADDR)) {
    Serial.println("BMP280 не знайдено за 0x76. Пробую 0x77...");
    if (!bmp.begin(0x77)) {
      Serial.println("Не знайдено ні за 0x76, ні за 0x77. Перевір дроти.");
      while (true) delay(1000);   // далі йти нема сенсу
    }
  }

  // Розумні налаштування для метеозадачі: помірне усереднення, рідкі виміри.
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
                  Adafruit_BMP280::SAMPLING_X2,    // температура ×2
                  Adafruit_BMP280::SAMPLING_X16,   // тиск ×16 (точніше)
                  Adafruit_BMP280::FILTER_X16,
                  Adafruit_BMP280::STANDBY_MS_500);
  Serial.println("BMP280 готовий.");
}

void loop() {
  float tempC = bmp.readTemperature();     // °C
  float presPa = bmp.readPressure();       // Па
  float presHpa = presPa / 100.0f;         // гПа (мілібари) — звичніші одиниці

  Serial.printf("t = %.2f °C   p = %.1f гПа\n", tempC, presHpa);
  delay(1000);
}
