#include "driver/adc.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define SENSOR_ADC_CHANNEL  ADC1_CHANNEL_6 // Вивід GPIO34 для ESP32
#define SAMPLING_PERIOD_MS  40             // Період узгоджений із циклом 38.3 мс

void sensor_reader_task(void *pvParameters) {
    // Налаштування розрядності АЦП 12 біт (0..4095)
    adc1_config_width(ADC_WIDTH_BIT_12);
    // Налаштування послаблення 11 дБ для діапазону до 3.3 В
    adc1_config_channel_atten(SENSOR_ADC_CHANNEL, ADC_ATTEN_DB_11);

    uint32_t filtered_val = 0;

    while (1) {
        int raw_sample = adc1_get_raw(SENSOR_ADC_CHANNEL);
        
        // Первинне експоненційне згладжування сигналу
        if (filtered_val == 0) {
            filtered_val = raw_sample;
        } else {
            filtered_val = (filtered_val * 3 + raw_sample) / 4;
        }

        // Затримка таски на час внутрішнього оновлення датчика
        vTaskDelay(pdMS_TO_TICKS(SAMPLING_PERIOD_MS));
    }
}
