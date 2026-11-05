#include <stdint.h>
#include <stdbool.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// Структура кільцевого буфера для обробки даних сенсора
typedef struct {
    uint8_t buffer[256];
    uint16_t head;
    uint16_t tail;
    portMUX_TYPE spinlock; // Апаратний спін-замок ESP-IDF
} safe_ring_buffer_t;

// Ініціалізація буфера та спин-замка
void ring_buffer_init(safe_ring_buffer_t *rb) {
    rb->head = 0;
    rb->tail = 0;
    vPortCPUInitializeMutex(&rb->spinlock);
}

// Запис байта в буфер із захистом критичної секції
bool ring_buffer_push(safe_ring_buffer_t *rb, uint8_t byte) {
    // Вхід у критичну секцію з вимкненням переривань і захопленням спін-замка
    taskENTER_CRITICAL(&rb->spinlock);

    uint16_t next_head = (rb->head + 1) % 256;
    if (next_head == rb->tail) {
        // Буфер переповнено, виходимо з критичної секції
        taskEXIT_CRITICAL(&rb->spinlock);
        return false;
    }

    rb->buffer[rb->head] = byte;
    rb->head = next_head;

    // Вихід з критичної секції та відновлення стану переривань
    taskEXIT_CRITICAL(&rb->spinlock);
    return true;
}
