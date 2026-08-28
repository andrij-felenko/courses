#include <WiFi.h>

// ADC1 на S3 — це GPIO1..GPIO10; беремо один із них.
#define ADC_PIN 3     // GPIO3 = ADC1_CH2 — придатний під активне радіо

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 2000) {}

  // Розширюємо діапазон входу до повних ~3.3 В (найбільше згасання сигналу).
  analogSetAttenuation(ADC_11db);

  // Вмикаємо Wi-Fi, щоб показати: на ADC1 виміри лишаються чистими.
  WiFi.mode(WIFI_STA);
  WiFi.begin("SSID", "PASSWORD");   // підстав свою мережу
  Serial.println("Wi-Fi піднято; читаю ADC1...");
}

void loop() {
  int raw = analogRead(ADC_PIN);              // 0..8191 (13 біт на S3!)
  uint32_t mv = analogReadMilliVolts(ADC_PIN); // одразу мілівольти, з калібруванням

  Serial.printf("сире = %4d   напруга = %u мВ (%.3f В)\n",
                raw, mv, mv / 1000.0f);
  delay(500);
}
