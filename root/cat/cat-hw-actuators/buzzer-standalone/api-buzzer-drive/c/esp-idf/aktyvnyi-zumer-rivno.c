#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define BUZ GPIO_NUM_18          // активний зумер висить прямо на виводі

void app_main(void) {
  gpio_config_t io = {
    .pin_bit_mask = 1ULL << BUZ,
    .mode         = GPIO_MODE_OUTPUT,
    .pull_up_en   = GPIO_PULLUP_DISABLE,
    .pull_down_en = GPIO_PULLDOWN_DISABLE,
    .intr_type    = GPIO_INTR_DISABLE,
  };
  gpio_config(&io);
  gpio_set_level(BUZ, 0);                 // на старті тиша

  while (1) {
    gpio_set_level(BUZ, 1);               // подали «плюс» → генератор завив
    vTaskDelay(pdMS_TO_TICKS(120));
    gpio_set_level(BUZ, 0);               // зняли → замовк
    vTaskDelay(pdMS_TO_TICKS(3000));
  }
}
