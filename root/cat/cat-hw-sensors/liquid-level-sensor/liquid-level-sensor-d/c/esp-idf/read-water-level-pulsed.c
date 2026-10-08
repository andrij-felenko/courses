// Приклад імпульсного живлення давача рівня для ESP-IDF (C)
#include "driver/gpio.h"
#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define SENSOR_POWER_GPIO GPIO_NUM_18
#define SENSOR_ADC_CHANNEL ADC_CHANNEL_6

int read_water_level_pulsed(adc_oneshot_unit_handle_t adc_handle) {
    gpio_set_level(SENSOR_POWER_GPIO, 1); // Увімкнути живлення електрода
    vTaskDelay(pdMS_TO_TICKS(5));         // Пауза 5 мм для стабілізації
    int raw_val = 0;
    adc_oneshot_read(adc_handle, SENSOR_ADC_CHANNEL, &raw_val);
    gpio_set_level(SENSOR_POWER_GPIO, 0); // Негайно вимкнути живлення
    return raw_val;
}
