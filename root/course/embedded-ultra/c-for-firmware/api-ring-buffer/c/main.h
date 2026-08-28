#ifndef STATIC_RING_BUFFER_H
#define STATIC_RING_BUFFER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// Конфігурація розміру буфера телеметрії (мусить бути 2^N)
#define RING_BUF_CAPACITY 256U
#define RING_BUF_MASK     (RING_BUF_CAPACITY - 1U)

_Static_assert((RING_BUF_CAPACITY & RING_BUF_MASK) == 0,
               "RING_BUF_CAPACITY must be a power of two!");

typedef struct {
    uint8_t buffer[RING_BUF_CAPACITY];
    volatile uint16_t head;
    volatile uint16_t tail;
} RingBuffer;

/**
 * @brief Ініціалізує кільцевий буфер перед початком роботи.
 * @param rb Покажчик на структуру буфера.
 */
void ring_buffer_init(RingBuffer *rb);

/**
 * @brief Додає байт у буфер. Безпечно для виклику з ISR виробника.
 * @param rb Покажчик на структуру буфера.
 * @param byte Значення байта.
 * @return true — байт збережено; false — буфер переповнено (дані відкинуто).
 */
bool ring_buffer_put(RingBuffer *rb, uint8_t byte);

/**
 * @brief Вичитує байт із буфера. Безпечно для виклику зі споживача.
 * @param rb Покажчик на структуру буфера.
 * @param byte Покажчик на вихідну змінну для збереження байта.
 * @return true — байт успішно вичитано; false — буфер порожній.
 */
bool ring_buffer_get(RingBuffer *rb, uint8_t *byte);

/**
 * @brief Перевіряє, чи буфер не містить даних.
 */
bool ring_buffer_is_empty(const RingBuffer *rb);

/**
 * @brief Перевіряє, чи заповнений буфер повністю.
 */
bool ring_buffer_is_full(const RingBuffer *rb);

/**
 * @brief Повертає поточну кількість байтів, готових до читання.
 */
uint16_t ring_buffer_available(const RingBuffer *rb);

#ifdef __cplusplus
}
#endif

#endif // STATIC_RING_BUFFER_H
