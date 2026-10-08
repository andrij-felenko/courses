#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_sleep.h"
#include "esp_log.h"

#define KEEPALIVE_PIN GPIO_NUM_25
#define SLEEP_DURATION_SEC 9

void app_main(void)
{
    // Налаштування виводу GPIO для керування транзисторним ключем
    gpio_reset_pin(KEEPALIVE_PIN);
    gpio_set_direction(KEEPALIVE_PIN, GPIO_MODE_OUTPUT);

    // Подача імпульсу струму 100 мА тривалістю 150 мс для скидання таймера MH-CD42
    gpio_set_level(KEEPALIVE_PIN, 1);
    vTaskDelay(pdMS_TO_TICKS(150));
    gpio_set_level(KEEPALIVE_PIN, 0);

    // Налаштування таймера глибокого сну на 9 секунд
    esp_sleep_enable_timer_wakeup(SLEEP_DURATION_SEC * 1000000ULL);
    
    // Перехід у режим deep-sleep
    esp_deep_sleep_start();
}
