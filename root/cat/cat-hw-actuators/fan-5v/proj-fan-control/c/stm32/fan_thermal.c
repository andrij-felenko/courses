// fan_thermal.c — швидкість за температурою + сторож обертів
#include "main.h"
#include <stdio.h>

extern TIM_HandleTypeDef htim1;  // TIM1_CH1 → PWM-вхід: PSC/ARR дають 25 кГц
extern TIM_HandleTypeDef htim3;  // TIM3 у режимі зовнішнього такту рахує імпульси TACH
                                 // (вхід TACH у CubeMX — з GPIO_PULLUP)

float read_temp_c(void);         // ← ваш давач (NTC, DS18B20, BME280)

static uint8_t temp_to_percent(float t) {
  const float tMin = 35.0f, tMax = 65.0f;
  if (t <= tMin) return 0;
  if (t >= tMax) return 100;
  return (uint8_t)((t - tMin) / (tMax - tMin) * 100.0f);
}

static void fan_set_speed(uint8_t percent) {          // деталі — у рецепті ШІМ
  if (percent > 100) percent = 100;
  uint32_t period = __HAL_TIM_GET_AUTORELOAD(&htim1) + 1;   // ARR+1 = повна швидкість
  __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, percent * period / 100);
}

void fan_thermal_run(void) {
  HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);   // 25-кГц несуча пішла
  HAL_TIM_Base_Start(&htim3);                 // лічильник імпульсів тахометра пішов
  uint8_t  dead_seconds = 0;    // скільки секунд поспіль наказ є, а обертів нема
  uint32_t last_ms = HAL_GetTick();

  for (;;) {
    if (HAL_GetTick() - last_ms < 1000) continue;   // один крок керування на секунду
    last_ms += 1000;

    float   t   = read_temp_c();
    uint8_t pct = temp_to_percent(t);
    fan_set_speed(pct);

    uint32_t count = __HAL_TIM_GET_COUNTER(&htim3);
    __HAL_TIM_SET_COUNTER(&htim3, 0);
    uint32_t rpm = (count / 2) * 60;   // ÷2 (2 імпульси/оберт) ×60 (у хвилини)

    // Сторож зі стартовою відстрочкою (нижче — чому не «в лоб»)
    if (pct > 0 && rpm == 0) { if (dead_seconds < 255) dead_seconds++; }
    else dead_seconds = 0;             // закрутився або наказ знято — лічильник у нуль
    if (dead_seconds >= 3) {           // 3 с наказу без жодного оберту — біда
      printf("!!! ТРИВОГА: наказано крутитися, а обертів нема\r\n");
      // тут: аварійний вихід, скид навантаження, зниження тактової тощо
    }

    printf("t=%.1f C  швидкість=%u%%  оберти=%lu об/хв\r\n", t, pct, (unsigned long)rpm);
  }
}
