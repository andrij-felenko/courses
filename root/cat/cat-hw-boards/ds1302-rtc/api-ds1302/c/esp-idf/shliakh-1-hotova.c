// Готового драйвера DS1302 в самому ESP-IDF нема: беруть спільнотний компонент
// ds1302 (esp-idf-lib) або власний тонкий модуль — ті самі ds_* із другої частини
// статті, загорнуті в стандартний struct tm.
#include <stdbool.h>
#include <time.h>
#include <sys/time.h>
#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_DAT  GPIO_NUM_27      // I/O  — двонапрямна
#define PIN_CLK  GPIO_NUM_14      // SCLK
#define PIN_RST  GPIO_NUM_26      // CE

static const char *TAG = "ds1302";

esp_err_t ds1302_write_protect(bool on);        // регістр 0x8E
esp_err_t ds1302_start(void);                   // скинути CH
esp_err_t ds1302_get_time(struct tm *t);        // burst-читання
esp_err_t ds1302_set_time(const struct tm *t);

void app_main(void) {
  gpio_config_t io = {
      .pin_bit_mask = (1ULL << PIN_CLK) | (1ULL << PIN_RST),
      .mode = GPIO_MODE_OUTPUT,
      .pull_up_en = GPIO_PULLUP_DISABLE,
      .pull_down_en = GPIO_PULLDOWN_DISABLE,
      .intr_type = GPIO_INTR_DISABLE,
  };
  ESP_ERROR_CHECK(gpio_config(&io));
  gpio_set_level(PIN_RST, 0);                   // сеанс закритий, поки не почали

  ESP_ERROR_CHECK(ds1302_write_protect(false)); // 1) без цього запис зникає мовчки
  ESP_ERROR_CHECK(ds1302_start());              // 2) скинути CH, інакше генератор стоїть

  struct tm t = {0};
  ESP_ERROR_CHECK(ds1302_get_time(&t));
  if (t.tm_year + 1900 < 2025) {                // 3) час недійсний — ставимо один раз
    ESP_LOGW(TAG, "час недійсний — ставлю стартове значення");
    struct tm init = { .tm_sec = 30, .tm_min = 47, .tm_hour = 10,
                       .tm_mday = 4, .tm_mon = 6, .tm_year = 126 };  // 2026-07-04 10:47:30
    ESP_ERROR_CHECK(ds1302_set_time(&init));
  }

  while (true) {
    ESP_ERROR_CHECK(ds1302_get_time(&t));
    // Крок, якого нема в Arduino-версії: віддати час системному годиннику —
    // далі його бачать мітки логу, звірка зі SNTP і вся стандартна time.h.
    struct timeval tv = { .tv_sec = mktime(&t), .tv_usec = 0 };
    settimeofday(&tv, NULL);

    char buf[24];
    strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", &t);
    ESP_LOGI(TAG, "%s", buf);
    vTaskDelay(pdMS_TO_TICKS(5000));            // читати раз на 5 с досить
  }
}
