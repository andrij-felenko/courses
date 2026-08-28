#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char *TAG = "ldr";
#define LDR_CHAN  ADC_CHANNEL_6     // GPIO34 — канал блоку ADC1
#define ALPHA     0.2f              // 0.1 гладше+лінивіше · 0.5 жвавіше+шумніше

void app_main(void) {
  adc_oneshot_unit_handle_t adc1;
  adc_oneshot_unit_init_cfg_t init = { .unit_id = ADC_UNIT_1 };
  ESP_ERROR_CHECK(adc_oneshot_new_unit(&init, &adc1));
  adc_oneshot_chan_cfg_t ch = { .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_12 };
  ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, LDR_CHAN, &ch));

  int raw = 0;
  ESP_ERROR_CHECK(adc_oneshot_read(adc1, LDR_CHAN, &raw));
  float smoothed = raw;             // засіяти першим відліком, а не нулем

  for (;;) {
    ESP_ERROR_CHECK(adc_oneshot_read(adc1, LDR_CHAN, &raw));
    smoothed += ALPHA * (raw - smoothed);   // y ← y + α·(нове − y)
    ESP_LOGI(TAG, "%d", (int)smoothed);
    vTaskDelay(pdMS_TO_TICKS(20));
  }
}
