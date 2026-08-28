#include "driver/ledc.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define SERVO_GPIO  18
#define PERIOD_US   20000               // 20 мс = 50 Гц
#define MAX_DUTY    65535               // лічильник 16 біт

static void servo_init(void) {
  ledc_timer_config_t t = {
    .speed_mode      = LEDC_LOW_SPEED_MODE,
    .duty_resolution = LEDC_TIMER_16_BIT,
    .timer_num       = LEDC_TIMER_0,
    .freq_hz         = 50,              // період 20 мс — головна умова
    .clk_cfg         = LEDC_AUTO_CLK,
  };
  ESP_ERROR_CHECK(ledc_timer_config(&t));

  ledc_channel_config_t c = {
    .gpio_num   = SERVO_GPIO,           // сигнальний дріт SG90
    .speed_mode = LEDC_LOW_SPEED_MODE,
    .channel    = LEDC_CHANNEL_0,
    .timer_sel  = LEDC_TIMER_0,
    .duty = 0, .hpoint = 0,
  };
  ESP_ERROR_CHECK(ledc_channel_config(&c));
}

static void servo_write_us(int us) {    // ширина імпульсу → код заповнення
  uint32_t duty = (uint32_t)((int64_t)us * MAX_DUTY / PERIOD_US);
  ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, duty);
  ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}

static void servo_write_deg(int deg) {  // градусів у залізі нема — рахуємо самі
  servo_write_us(1000 + deg * (2000 - 1000) / 180);
}

void app_main(void) {
  servo_init();
  while (1) {
    servo_write_deg(0);   vTaskDelay(pdMS_TO_TICKS(1000));  // одне крайнє
    servo_write_deg(90);  vTaskDelay(pdMS_TO_TICKS(1000));  // нейтраль
    servo_write_deg(180); vTaskDelay(pdMS_TO_TICKS(1000));  // інше крайнє
  }
}
