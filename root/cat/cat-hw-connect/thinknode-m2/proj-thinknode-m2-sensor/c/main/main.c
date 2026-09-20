#include <stdio.h>
#include <string.h>
#include "esp_sleep.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sx1262.h"

#define SLEEP_TIME_SEC 60

static const char *TAG = "MAIN";

static float read_temperature_sensor(void) {
    // У реальному проєкті тут опитування I2C/ADC
    return 24.5f; 
}

void app_main(void) {
    ESP_LOGI(TAG, "Wake up! Initiating node work cycle.");

    if (!sx1262_init()) {
        ESP_LOGE(TAG, "SX1262 initialization failed");
    } else {
        float temp = read_temperature_sensor();
        
        char payload[32];
        snprintf(payload, sizeof(payload), "{\"t\": %.1f}", temp);
        
        ESP_LOGI(TAG, "Sending data: %s", payload);
        sx1262_transmit((const uint8_t *)payload, strlen(payload));
        
        // Чекаємо завершення відправки (в ідеалі варто обробляти переривання від DIO1)
        vTaskDelay(pdMS_TO_TICKS(500));
    }

    ESP_LOGI(TAG, "Entering deep sleep for %d seconds...", SLEEP_TIME_SEC);
    esp_sleep_enable_timer_wakeup(SLEEP_TIME_SEC * 1000000ULL);
    esp_deep_sleep_start();
}
