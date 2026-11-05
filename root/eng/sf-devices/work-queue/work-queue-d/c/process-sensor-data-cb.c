#include <stdint.h>
#include <stdbool.h>
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"

// Тип функції зворотного виклику для відкладеної роботи
typedef void (*work_func_t)(void *arg);

// Структура елемента черги робіт
typedef struct {
    work_func_t func;  // Вказівник на функцію-обробник
    void *arg;         // Вказівник на контекст даних
} work_item_t;

// Контекст події давача
typedef struct {
    uint32_t timestamp;
    uint16_t raw_value;
} sensor_event_t;

// Статичний об'єкт події для уникнення динамічної пам'яті у перериванні
static sensor_event_t g_sensor_data;
static work_item_t g_sensor_work_item;

// Обробник відкладеної роботи (виконується в контексті робочого потоку)
void process_sensor_data_cb(void *arg) {
    sensor_event_t *event = (sensor_event_t *)arg;
    if (event != NULL) {
        // Тривала обробка: фільтрація, переведення у фізичні величини
        (void)event->raw_value;
    }
}

// Ініціалізація елемента роботи
void init_sensor_work(void) {
    g_sensor_work_item.func = process_sensor_data_cb;
    g_sensor_work_item.arg = &g_sensor_data;
}

// Безпечна постановка елемента з ISR (FreeRTOS)
bool submit_work_from_isr(QueueHandle_t queue_handle, BaseType_t *higher_priority_woken) {
    g_sensor_data.timestamp = xTaskGetTickCountFromISR();
    g_sensor_data.raw_value = 0x03FF; // Зчитано з апаратного регістра

    return xQueueSendFromISR(queue_handle, &g_sensor_work_item, higher_priority_woken) == pdTRUE;
}
