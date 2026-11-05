// C: Неблокуючий обробник елемента черги робіт для RTOS
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

typedef struct {
    SemaphoreHandle_t bus_mutex;
    uint8_t sensor_addr;
    uint8_t rx_data[8];
    volatile bool is_busy;
} sensor_work_context_t;

// Правильний неблокуючий callback для системної черги робіт
void sensor_work_callback(void *arg) {
    sensor_work_context_t *ctx = (sensor_work_context_t *)arg;

    // Спроба захопити мутекс без блокування потоку-виконавця (таймаут 0)
    if (xSemaphoreTake(ctx->bus_mutex, 0) == pdTRUE) {
        // Ресурс вільний: виконуємо швидку вибірку даних з апаратного буфера
        for (int i = 0; i < 8; i++) {
            ctx->rx_data[i] = 0xAA; // Імітація зчитування регістра
        }
        ctx->is_busy = false;
        xSemaphoreGive(ctx->bus_mutex);
    } else {
        // Ресурс зайнятий: не чекаємо! Повертаємо керування, щоб не блокувати чергу
        ctx->is_busy = true;
    }
}
