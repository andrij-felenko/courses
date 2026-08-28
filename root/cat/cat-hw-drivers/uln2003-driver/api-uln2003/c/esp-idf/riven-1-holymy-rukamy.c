#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// GPIO, куди підключені входи плати ULN2003
#define IN1 GPIO_NUM_18
#define IN2 GPIO_NUM_19
#define IN3 GPIO_NUM_21
#define IN4 GPIO_NUM_22

// Вісім станів half-step. Рядок — один такт; стовпці — IN1..IN4.
// 1 = обмотку під струмом (вхід у 1), 0 = знеструмлено.
static const uint8_t seq[8][4] = {
  {1, 0, 0, 0},   // крок 1
  {1, 1, 0, 0},   // крок 2
  {0, 1, 0, 0},   // крок 3
  {0, 1, 1, 0},   // крок 4
  {0, 0, 1, 0},   // крок 5
  {0, 0, 1, 1},   // крок 6
  {0, 0, 0, 1},   // крок 7
  {1, 0, 0, 1},   // крок 8
};

void app_main(void) {
  gpio_config_t io = {
    .pin_bit_mask = (1ULL << IN1) | (1ULL << IN2) | (1ULL << IN3) | (1ULL << IN4),
    .mode         = GPIO_MODE_OUTPUT,
    .pull_up_en   = GPIO_PULLUP_DISABLE,
    .pull_down_en = GPIO_PULLDOWN_DISABLE,
    .intr_type    = GPIO_INTR_DISABLE,
  };
  ESP_ERROR_CHECK(gpio_config(&io));
}
