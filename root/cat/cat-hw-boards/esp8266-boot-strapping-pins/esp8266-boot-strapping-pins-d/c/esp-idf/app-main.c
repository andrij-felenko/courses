#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"

#define SHARED_BOOT_PIN GPIO_NUM_0

void app_main(void) {
  // Затримка 100 мс для завершення процедури latching завантажувача
  vTaskDelay(pdMS_TO_TICKS(100));

  gpio_config_t io_conf = {
    .pin_bit_mask = (1ULL << SHARED_BOOT_PIN),
    .mode = GPIO_MODE_INPUT,
    .pull_up_en = GPIO_PULLUP_ENABLE,
    .pull_down_en = GPIO_PULLDOWN_DISABLE,
    .intr_type = GPIO_INTR_DISABLE
  };
  gpio_config(&io_conf);
}
