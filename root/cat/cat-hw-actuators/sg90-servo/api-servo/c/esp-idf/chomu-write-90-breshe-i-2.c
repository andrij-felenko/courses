#include "driver/uart.h"
#include "esp_log.h"
#include <stdlib.h>

static const char *TAG = "servo";

// Калібрувальні межі КОНКРЕТНОГО серва — знайдені дослідом (див. нижче).
#define US_MIN 1000                 // ширина для 0°
#define US_MAX 2000                 // ширина для 180°

// Наш власний перерахунок кут → мікросекунди за ВІДКАЛІБРОВАНИМИ межами.
static int deg_to_us(int deg) {
  if (deg < 0)   deg = 0;
  if (deg > 180) deg = 180;
  return US_MIN + deg * (US_MAX - US_MIN) / 180;   // лінійно між нашими межами
}

void app_main(void) {
  servo_init();
  uart_driver_install(UART_NUM_0, 256, 0, 0, NULL, 0);   // консольний UART на читання

  uint8_t buf[16];
  while (1) {
    // Приймаємо кут із консолі: надішліть число 0..180 і Enter.
    int n = uart_read_bytes(UART_NUM_0, buf, sizeof(buf) - 1, pdMS_TO_TICKS(100));
    if (n <= 0) continue;
    buf[n] = 0;
    int deg = atoi((char *)buf);
    if (deg < 0 || deg > 180) continue;
    servo_write_us(deg_to_us(deg));
    ESP_LOGI(TAG, "кут %d° -> %d мкс", deg, deg_to_us(deg));
  }
}
