#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define BUZ GPIO_NUM_18                    // вивід, на якому висить активний зумер

static void buz_init(void) {
  gpio_config_t cfg = {
    .pin_bit_mask = 1ULL << BUZ,
    .mode         = GPIO_MODE_OUTPUT,      // просто вихід, ніякої периферії
    .pull_up_en   = GPIO_PULLUP_DISABLE,
    .pull_down_en = GPIO_PULLDOWN_DISABLE,
    .intr_type    = GPIO_INTR_DISABLE,
  };
  ESP_ERROR_CHECK(gpio_config(&cfg));
}

static void beep(uint32_t ms) {            // короткий сигнал «сталася подія»
  gpio_set_level(BUZ, 1);                  // подали живлення — генератор усередині завив
  vTaskDelay(pdMS_TO_TICKS(ms));
  gpio_set_level(BUZ, 0);                  // зняли — замовк
}

void app_main(void) {
  buz_init();
  while (1) {
    beep(120);                             // піп
    vTaskDelay(pdMS_TO_TICKS(2000));
  }
}
