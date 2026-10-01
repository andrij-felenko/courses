/*
 * Тестова програма перевірки автономного завантаження ESP8266 (SPI Flash Boot).
 * Забезпечує конфігурацію GPIO2, виведення логів через UART та циклічне миготіння світлодіодом.
 */

#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_log.h"

// Номер виводу GPIO, до якого підключено світлодіод (GPIO2 відповідає вбудованому світлодіоду на ESP-01)
#define BLINK_GPIO GPIO_NUM_2
// Період перемикання стану світлодіода в мілісекундах
#define BLINK_PERIOD_MS 1000

static const char *TAG = "BOOT_CHECK";

// Задача FreeRTOS для миготіння світлодіодом та відправки логів
static void blink_task(void *pvParameters)
{
    // Налаштування виводу GPIO на вихід без підтяжок
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << BLINK_GPIO),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);

    uint32_t level = 0;
    ESP_LOGI(TAG, "Автономний режим SPI Flash Boot підтверджено. Розпочато роботу циклу миготіння.");

    while (1) {
        // Зміна стану лінії GPIO та виведення статусу в послідовний порт
        gpio_set_level(BLINK_GPIO, level);
        ESP_LOGI(TAG, "Стан світлодіода: %s (рівень GPIO%d: %u)", 
                 level ? "УВІМКНЕНО" : "ВИМКНЕНО", BLINK_GPIO, (unsigned int)level);
        
        level = !level;
        // Затримка виконання задачі на 1 секунду
        vTaskDelay(pdMS_TO_TICKS(BLINK_PERIOD_MS));
    }
}

void app_main(void)
{
    // Повідомлення про успішний перехід ROM-завантажувача до виконання прошивки з Flash
    ESP_LOGI(TAG, "Ініціалізація системи ESP8266 після відновлення живлення або скидання.");
    
    // Створення задачі FreeRTOS з пріоритетом 5 та розміром стеку 2048 байтів
    xTaskCreate(blink_task, "blink_task", 2048, NULL, 5, NULL);
}
