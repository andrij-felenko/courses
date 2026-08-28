// fan_thermal.c — швидкість за температурою + сторож обертів
#include "driver/ledc.h"
#include "driver/pulse_cnt.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char *TAG = "fan";
#define PWM_PIN   25
#define PWM_FREQ  25000              // 25 кГц — генерацію див. у рецепті ШІМ
#define DUTY_MAX  255                // 8 біт

static pcnt_unit_handle_t unit;      // лічильник обертів (налаштування — у рецепті TACH)

float read_temp_c(void);                       // ← ваш давач (NTC, DS18B20, BME280)
void  tach_pcnt_begin(pcnt_unit_handle_t *out); // ← вхід TACH із підтяжкою + PCNT

static uint8_t temp_to_percent(float t) {
  const float tMin = 35.0f, tMax = 65.0f;
  if (t <= tMin) return 0;
  if (t >= tMax) return 100;
  return (uint8_t)((t - tMin) / (tMax - tMin) * 100.0f);
}

static void fan_pwm_begin(void) {              // деталі — у рецепті ШІМ
  ledc_timer_config_t tm = { .speed_mode = LEDC_LOW_SPEED_MODE, .timer_num = LEDC_TIMER_0,
                             .duty_resolution = LEDC_TIMER_8_BIT,
                             .freq_hz = PWM_FREQ, .clk_cfg = LEDC_AUTO_CLK };
  ESP_ERROR_CHECK(ledc_timer_config(&tm));
  ledc_channel_config_t ch = { .gpio_num = PWM_PIN, .speed_mode = LEDC_LOW_SPEED_MODE,
                               .channel = LEDC_CHANNEL_0, .timer_sel = LEDC_TIMER_0,
                               .duty = 0, .hpoint = 0 };
  ESP_ERROR_CHECK(ledc_channel_config(&ch));
}

static void fan_set_speed(uint8_t percent) {
  if (percent > 100) percent = 100;
  ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, percent * DUTY_MAX / 100);
  ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}

void app_main(void) {
  fan_pwm_begin();
  tach_pcnt_begin(&unit);
  uint8_t dead_seconds = 0;          // скільки секунд поспіль наказ є, а обертів нема

  for (;;) {
    vTaskDelay(pdMS_TO_TICKS(1000)); // один крок керування на секунду

    float   t   = read_temp_c();
    uint8_t pct = temp_to_percent(t);
    fan_set_speed(pct);

    int count = 0;
    pcnt_unit_get_count(unit, &count);
    pcnt_unit_clear_count(unit);
    uint32_t rpm = (count / 2) * 60; // ÷2 (2 імпульси/оберт) ×60 (у хвилини)

    // Сторож зі стартовою відстрочкою (нижче — чому не «в лоб»)
    if (pct > 0 && rpm == 0) { if (dead_seconds < 255) dead_seconds++; }
    else dead_seconds = 0;           // закрутився або наказ знято — лічильник у нуль
    if (dead_seconds >= 3) {         // 3 с наказу без жодного оберту — біда
      ESP_LOGE(TAG, "ТРИВОГА: наказано крутитися, а обертів нема — перевір вентилятор");
      // тут: аварійний вихід, скид навантаження, зниження тактової тощо
    }

    ESP_LOGI(TAG, "t=%.1f°C  швидкість=%u%%  оберти=%u об/хв", t, pct, (unsigned)rpm);
  }
}
