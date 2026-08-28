#include "driver/gpio.h"
#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define LDR_CHAN   ADC_CHANNEL_6    // GPIO34
#define PIN_LED    GPIO_NUM_2

#define DARK_ON    1200   // темніше цього → УВІМКНУТИ (нижній поріг, 12 біт)
#define LIGHT_OFF  1600   // світліше цього → ВИМКНУТИ (верхній поріг)

void app_main(void) {
  gpio_config_t io = { .pin_bit_mask = 1ULL << PIN_LED, .mode = GPIO_MODE_OUTPUT };
  ESP_ERROR_CHECK(gpio_config(&io));

  adc_oneshot_unit_handle_t adc1;
  adc_oneshot_unit_init_cfg_t init = { .unit_id = ADC_UNIT_1 };
  ESP_ERROR_CHECK(adc_oneshot_new_unit(&init, &adc1));
  adc_oneshot_chan_cfg_t ch = { .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_12 };
  ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, LDR_CHAN, &ch));

  bool lamp_on = false;             // поточний стан — частина рішення!
  for (;;) {
    int light = 0;                  // (краще — уже згладжений; див. збірку нижче)
    ESP_ERROR_CHECK(adc_oneshot_read(adc1, LDR_CHAN, &light));

    if (!lamp_on && light < DARK_ON)       lamp_on = true;   // було світло, стало темно
    else if (lamp_on && light > LIGHT_OFF) lamp_on = false;  // було темно, стало світло
    // якщо відлік між порогами — жодна умова не спрацює, стан лишається

    gpio_set_level(PIN_LED, lamp_on);
    vTaskDelay(pdMS_TO_TICKS(50));
  }
}
