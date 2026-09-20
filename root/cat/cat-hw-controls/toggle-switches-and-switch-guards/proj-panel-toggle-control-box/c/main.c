#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "esp_log.h"
#include "toggle_switch.h"

static const char *TAG = "MAIN_APP";

// Задача FreeRTOS для обробки подій перемикання тумблера під ковпачком
static void toggle_switch_task(void *pvParameters) {
    QueueHandle_t queue = (QueueHandle_t)pvParameters;
    toggle_switch_event_t event;

    while (1) {
        if (xQueueReceive(queue, &event, portMAX_DELAY) == pdTRUE) {
            const char *state_str = "НЕВИЗНАЧЕНО";
            switch (event.current_state) {
                case TOGGLE_STATE_OFF: state_str = "OFF (Центр)"; break;
                case TOGGLE_STATE_ON1: state_str = "ON1 (Верхній режим)"; break;
                case TOGGLE_STATE_ON2: state_str = "ON2 (Нижній режим)"; break;
                case TOGGLE_STATE_INVALID: state_str = "ПОМИЛКА ЛІНІЇ"; break;
            }

            ESP_LOGW(TAG, "[ПОДІЯ ТУМБЛЕРА] Час: %lu мс | Новий стан: %s", 
                     (unsigned long)event.timestamp_ms, state_str);
        }
    }
}

void app_main(void) {
    ESP_LOGI(TAG, "Запуск системи опитування тумблерів з ковпачком Mollie Guard...");

    // 1. Створення черги FreeRTOS для подій
    QueueHandle_t event_queue = xQueueCreate(10, sizeof(toggle_switch_event_t));

    // 2. Конфігурація 3-позиційного тумблера на GPIO4 та GPIO5
    toggle_switch_config_t config = {
        .pin_on1 = GPIO_NUM_4,
        .pin_on2 = GPIO_NUM_5,
        .debounce_ms = 25,
        .active_low = true // Активний LOW з внутрішньою підтяжкою PULLUP
    };

    toggle_switch_handle_t switch_handle = NULL;
    esp_err_t err = toggle_switch_init(&config, event_queue, &switch_handle);

    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації тумблера!");
        return;
    }

    // 3. Запуск задачі обробки подій у FreeRTOS
    xTaskCreate(toggle_switch_task, "toggle_task", 3072, event_queue, 10, NULL);

    ESP_LOGI(TAG, "Система працює у неблокувальному режимі.");
}
