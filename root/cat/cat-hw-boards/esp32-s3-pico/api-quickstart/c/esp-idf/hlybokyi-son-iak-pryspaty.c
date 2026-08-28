#include "esp_sleep.h"
#include "esp_log.h"

void app_main(void) {
  // 1) корисна робота: тут прокидання, вимір, відправка в мережу…
  ESP_LOGI("sleep", "прокинувся, роблю вимір");

  // 2) наказуємо RTC-таймеру розбудити нас через 60 секунд
  esp_sleep_enable_timer_wakeup(60ULL * 1000000ULL);   // аргумент — у мікросекундах

  // 3) засинаємо; наступний рядок ніколи не виконається —
  //    після сну буде новий старт із app_main()
  ESP_LOGI("sleep", "засинаю на 60 с");
  vTaskDelay(pdMS_TO_TICKS(50));     // договорити журнал, поки USB живий
  esp_deep_sleep_start();
}
