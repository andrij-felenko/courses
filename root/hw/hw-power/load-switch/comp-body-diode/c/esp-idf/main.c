// Те саме на ESP-IDF: затвор — через driver/gpio.h, вихід — через oneshot-АЦП.
#include "driver/gpio.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

gpio_set_level(LOAD_EN, 0);                  // закрили канал ключа
vTaskDelay(pdMS_TO_TICKS(10));               // даємо ємності стекти

int raw = 0, mv = 0;                         // adc/cali — заведені при ініціалізації
ESP_ERROR_CHECK(adc_oneshot_read(adc, VOUT_SENSE_CH, &raw));
ESP_ERROR_CHECK(adc_cali_raw_to_voltage(cali, raw, &mv));
if (mv > VOUT_OFF_THRESHOLD_MV) {
    // канал закритий, а напруга лишилась → тече крізь body-діод (зворотне живлення)
    // повне відключення тут потребує ключа з reverse current blocking
    ESP_LOGW(TAG, "vyhid ne znyksya: %d mV — mozhlyve zhyvlennya kriz body-diod", mv);
}
