#include "driver/rtc_io.h"

const gpio_num_t PIN_REED = GPIO_NUM_25;  // ОБОВ'ЯЗКОВО RTC-здатний GPIO!

void setup() {
  Serial.begin(115200);
  delay(200);

  // чому прокинулись цього разу?
  esp_sleep_wakeup_cause_t cause = esp_sleep_get_wakeup_cause();
  if (cause == ESP_SLEEP_WAKEUP_EXT0)
    Serial.println("прокинувся: геркон замкнувся (магніт поряд)");
  else
    Serial.println("холодний старт / скидання");

  // тут — корисне діло: надіслати тривогу по Wi-Fi, інкрементувати лічбу тощо

  // готуємось спати: будити, коли PIN_REED впаде в 0 (геркон замкнений)
  esp_sleep_enable_ext0_wakeup(PIN_REED, 0);   // 0 == прокинутись на LOW

  // на час сну лишити внутрішню підтяжку, щоб пін не «плавав»
  rtc_gpio_pullup_en(PIN_REED);
  rtc_gpio_pulldown_dis(PIN_REED);

  Serial.println("засинаю…");
  Serial.flush();
  esp_deep_sleep_start();                        // ← далі виконання НЕ ЙДЕ
}

void loop() {
  // недосяжно: після deep sleep чип перезавантажується й починає із setup()
}
