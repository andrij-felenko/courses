#include "main.h"
#include <stdbool.h>

typedef struct {
  ADC_HandleTypeDef *adc;
  int   raw_min, raw_max;     // межі власного діапазону (калібрування)
  float smoothed;             // згладжена оцінка (EMA)
  float alpha;                // сила фільтра 0..1
  bool  dark;                 // поточний стан (для гістерезису)
  int   on_pct, off_pct;      // пороги у ВІДСОТКАХ діапазону
} light_sensor_t;

static uint16_t light_raw(light_sensor_t *s) {
  HAL_ADC_Start(s->adc);
  HAL_ADC_PollForConversion(s->adc, 10);
  uint16_t v = HAL_ADC_GetValue(s->adc);
  HAL_ADC_Stop(s->adc);
  return v;
}

// full_scale: 4095 для 12-бітного АЦП (типове для STM32), 1023 для 10-бітного режиму
void light_begin(light_sensor_t *s, ADC_HandleTypeDef *adc,
                 int full_scale, float alpha, int on_pct, int off_pct) {
  s->adc = adc;  s->alpha = alpha;
  s->on_pct = on_pct;  s->off_pct = off_pct;  s->dark = false;
  s->raw_min = full_scale;    // «перевернуті» старти під пошук min/max
  s->raw_max = 0;
  s->smoothed = light_raw(s); // засіяти фільтр першим відліком
}

// покрутіть освітлення протягом seconds — функція зловить ваші крайнощі
void light_calibrate(light_sensor_t *s, uint16_t seconds) {
  uint32_t until = HAL_GetTick() + (uint32_t)seconds * 1000;
  while (HAL_GetTick() < until) {
    int v = light_raw(s);
    if (v < s->raw_min) s->raw_min = v;
    if (v > s->raw_max) s->raw_max = v;
    HAL_Delay(5);
  }
  if (s->raw_max - s->raw_min < 20) {   // діапазон підозріло вузький — калібрування недійсне
    s->raw_min = 0;  s->raw_max = 0;    // (нуль-нуль = «не відкалібровано»)
  }
}

int light_update(light_sensor_t *s) {   // кликати щоцикл: оновлює фільтр
  int raw = light_raw(s);
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
