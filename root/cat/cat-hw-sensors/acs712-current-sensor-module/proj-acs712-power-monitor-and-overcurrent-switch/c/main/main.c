#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "acs712_driver.h"

static const char *TAG = "MAIN";

void sensor_task(void *pvParameters) {
    acs712_handle_t sensor;
    acs712_config_t config = {
        .adc_channel = ADC_CHANNEL_6, // GPIO34
        .type = ACS712_TYPE_05B,
        .relay_gpio = GPIO_NUM_25,
        .vcc = 3.3f,
        .overcurrent_limit_a = 4.0f,
        .hysteresis_a = 0.5f,
    };

    ESP_ERROR_CHECK(acs712_init(&sensor, &config));

    ESP_LOGI(TAG, "Калібрування нуля при відсутності струму...");
    acs712_calibrate_zero(&sensor, 100);

    while (1) {
        float rms_current = 0.0f;
        esp_err_t ret = acs712_read_current_rms(&sensor, 50.0f, &rms_current);
        if (ret == ESP_OK) {
            float power_w = rms_current * 230.0f;
            ESP_LOGI(TAG, "Струм RMS: %.2f A | Потужність: %.1f Вт", rms_current, power_w);
            acs712_check_protection(&sensor, rms_current);
        } else {
            ESP_LOGE(TAG, "Помилка зчитування АЦП: %s", esp_err_to_name(ret));
        }

        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

void app_main(void) {
    ESP_LOGI(TAG, "Запуск додатка моніторингу струму ACS712 в ESP-IDF");
    xTaskCreate(sensor_task, "sensor_task", 4096, NULL, 5, NULL);
}
