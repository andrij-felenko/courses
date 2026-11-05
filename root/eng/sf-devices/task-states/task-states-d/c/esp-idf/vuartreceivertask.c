#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "esp_log.h"

static const char *TAG = "UART_WAIT";
static QueueHandle_t xUartQueue;

// Задача очікування даних із черги з таймаутом
void vUartReceiverTask(void *pvParameters) {
    uint8_t rxByte;
    // Граничний час очікування: 500 мілісекунд
    const TickType_t xTimeoutTicks = pdMS_TO_TICKS(500);

    while (1) {
        // Задача звертається до черги. Якщо черга порожня, задача
        // переходить у стан Blocked і звільняє процесор.
        if (xQueueReceive(xUartQueue, &rxByte, xTimeoutTicks) == pdTRUE) {
            // Успішно отримано байт до закінчення таймауту
            ESP_LOGI(TAG, "Отримано байт: 0x%02X", rxByte);
        } else {
            // Таймаут вичерпано, а нові дані не надійшли
            ESP_LOGW(TAG, "Таймаут очікування даних з UART!");
            // Задача може виконати перевірку стану периферії
        }
    }
}
