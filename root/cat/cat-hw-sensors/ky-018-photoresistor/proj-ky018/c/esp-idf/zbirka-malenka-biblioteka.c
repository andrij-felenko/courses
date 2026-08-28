#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

typedef struct {
  adc_oneshot_unit_handle_t adc;
  adc_channel_t chan;
  int   raw_min, raw_max;     // межі власного діапазону (калібрування)
  float smoothed;             // згладжена оцінка (EMA)
  float alpha;                // сила фільтра 0..1
  bool  dark;                 // поточний стан (для гістерезису)
  int   on_pct, off_pct;      // пороги у ВІДСОТКАХ діапазону
} light_sensor_t;

// full_scale: 4095 для 12-бітного АЦП ESP32
void light_begin(light_sensor_t *s, adc_oneshot_unit_handle_t adc, adc_channel_t chan,
                 int full_scale, float alpha, int on_pct, int off_pct) {
  s->adc = adc;  s->chan = chan;  s->alpha = alpha;
  s->on_pct = on_pct;  s->off_pct = off_pct;  s->dark = false;
  s->raw_min = full_scale;    // «перевернуті» старти під пошук min/max
  s->raw_max = 0;
  int raw = 0;
  ESP_ERROR_CHECK(adc_oneshot_read(adc, chan, &raw));
  s->smoothed = raw;          // засіяти фільтр першим відліком
}

// покрутіть освітлення протягом seconds — функція зловить ваші крайнощі
void light_calibrate(light_sensor_t *s, uint16_t seconds) {
  TickType_t until = xTaskGetTickCount() + pdMS_TO_TICKS(seconds * 1000);
  while (xTaskGetTickCount() < until) {
    int v = 0;
    ESP_ERROR_CHECK(adc_oneshot_read(s->adc, s->chan, &v));
    if (v < s->raw_min) s->raw_min = v;
    if (v > s->raw_max) s->raw_max = v;
    vTaskDelay(pdMS_TO_TICKS(5));
  }
  if (s->raw_max - s->raw_min < 20) {   // діапазон підозріло вузький — калібрування недійсне
    s->raw_min = 0;  s->raw_max = 0;    // (нуль-нуль = «не відкалібровано»)
  }
}

int light_update(light_sensor_t *s) {   // кликати щоцикл: оновлює фільтр
  int raw = 0;
  ESP_ERROR_CHECK(adc_oneshot_read(s->adc, s->chan, &raw));
  s->smoothed += s->alpha * (raw - s->smoothed);
  return (int)s->smoothed;
}

uint8_t light_percent(const light_sensor_t *s) {  // 0..100 % власного діапазону
  if (s->raw_max <= s->raw_min) return 0;         // ще не відкалібровано
  int v = (int)s->smoothed;
  if (v <= s->raw_min) return 0;
  if (v >= s->raw_max) return 100;
  return (uint32_t)(v - s->raw_min) * 100 / (s->raw_max - s->raw_min);
}

bool light_is_dark(light_sensor_t *s) {           // рішення з гістерезисом, у відсотках
  uint8_t p = light_percent(s);
  if (!s->dark && p < s->on_pct)       s->dark = true;    // стало темно
  else if (s->dark && p > s->off_pct)  s->dark = false;   // стало світло
  return s->dark;
}
