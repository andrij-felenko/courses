// Те саме на ESP-IDF: затвор — driver/gpio.h, вихід — oneshot-АЦП.
#include "driver/gpio.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

gpio_set_level(SWITCH_EN, 0);                 // закрили канал
vTaskDelay(pdMS_TO_TICKS(10));                // даємо ємності стекти

int raw = 0, mv = 0;                          // adc/cali заведені при ініціалізації
ESP_ERROR_CHECK(adc_oneshot_read(adc, VOUT_SENSE_CH, &raw));
ESP_ERROR_CHECK(adc_cali_raw_to_voltage(cali, raw, &mv));
if (mv > VOUT_OFF_THRESHOLD_MV) {
    // канал закрито, а напруга є → тече крізь body-діод (зворотне живлення)
    ESP_LOGW(TAG, "vyhid ne znyksya: %d mV — mozhlyve zhyvlennya kriz body-diod", mv);
}
