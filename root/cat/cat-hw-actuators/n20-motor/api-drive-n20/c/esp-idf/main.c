// N20 через DRV8833, канал A. ESP32, ESP-IDF. ШІМ — через периферію LEDC.
#include "driver/gpio.h"
#include "driver/ledc.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char *TAG = "n20";

#define AIN1      GPIO_NUM_25          // будь-який GPIO можна віддати LEDC-каналу
#define AIN2      GPIO_NUM_26
#define SLP       GPIO_NUM_27          // nSLEEP драйвера
#define PWM_RES   LEDC_TIMER_10_BIT    // роздільність 10 біт
#define PWM_MAX   1023                 // → шпаруватість 0..1023
#define CH1       LEDC_CHANNEL_0       // LEDC-канал під AIN1
#define CH2       LEDC_CHANNEL_1       // LEDC-канал під AIN2

static void set_duty(ledc_channel_t ch, uint32_t duty) {
  ledc_set_duty(LEDC_LOW_SPEED_MODE, ch, duty);
  ledc_update_duty(LEDC_LOW_SPEED_MODE, ch);   // без цього нове значення не поїде
}

static void motor_coast(void) { set_duty(CH1, 0); set_duty(CH2, 0); }              // 0 0 → вибіг
static void motor_brake(void) { set_duty(CH1, PWM_MAX); set_duty(CH2, PWM_MAX); }  // 1 1 → гальмо

// «Фазна» схема: один канал у 0, на другий кладемо ШІМ-швидкість.
static void motor_drive(int speed) {
  if (speed >  100) speed =  100;
  if (speed < -100) speed = -100;
  uint32_t duty = (uint32_t)(speed < 0 ? -speed : speed) * PWM_MAX / 100;
  if (speed >= 0) { set_duty(CH2, 0); set_duty(CH1, duty); }   // ВПЕРЕД
  else            { set_duty(CH1, 0); set_duty(CH2, duty); }   // НАЗАД
}

static void motor_init(void) {
  gpio_config_t slp = {                        // nSLEEP — звичайний вихід
      .pin_bit_mask = 1ULL << SLP,
      .mode = GPIO_MODE_OUTPUT,
  };
  ESP_ERROR_CHECK(gpio_config(&slp));
  gpio_set_level(SLP, 1);                      // будимо драйвер

  ledc_timer_config_t tim = {                  // спільний таймер для обох каналів
      .speed_mode      = LEDC_LOW_SPEED_MODE,
      .timer_num       = LEDC_TIMER_0,
      .duty_resolution = PWM_RES,
      .freq_hz         = 20000,                // 20 кГц — вище чутного
      .clk_cfg         = LEDC_AUTO_CLK,
  };
  ESP_ERROR_CHECK(ledc_timer_config(&tim));

  ledc_channel_config_t ch = {                 // прив'язуємо піни драйвера до каналів
      .speed_mode = LEDC_LOW_SPEED_MODE,
      .timer_sel  = LEDC_TIMER_0,
      .intr_type  = LEDC_INTR_DISABLE,
      .duty = 0, .hpoint = 0,
      .channel = CH1, .gpio_num = AIN1,
  };
  ESP_ERROR_CHECK(ledc_channel_config(&ch));
  ch.channel = CH2; ch.gpio_num = AIN2;
  ESP_ERROR_CHECK(ledc_channel_config(&ch));

  motor_coast();                               // старт у безпечному стані
  ESP_LOGI(TAG, "драйвер розбуджено, мотор відпущено");
}

void app_main(void) {
  motor_init();
  while (1) {
    for (int s = 0; s <= 100; s++) { motor_drive(s); vTaskDelay(pdMS_TO_TICKS(20)); }
    vTaskDelay(pdMS_TO_TICKS(1000));
    motor_brake();
    vTaskDelay(pdMS_TO_TICKS(500));
    for (int s = 0; s >= -100; s--) { motor_drive(s); vTaskDelay(pdMS_TO_TICKS(20)); }
    vTaskDelay(pdMS_TO_TICKS(1000));
    motor_coast();
    vTaskDelay(pdMS_TO_TICKS(1500));
  }
}
