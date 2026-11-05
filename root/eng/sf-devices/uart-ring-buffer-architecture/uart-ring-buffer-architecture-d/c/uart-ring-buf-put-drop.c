#include <stdint.h>
#include <stdbool.h>

// Припускаємо використання CMSIS для ARM Cortex-M або аналог для бар'єра пам'яті
#if defined(__ARM_ARCH)
  #include <cmsis_compiler.h>
#else
  #define __DMB() __asm volatile("" ::: "memory") // Бар'єр компілятора як fallback
#endif

#define UART_BUF_SIZE 128U
#define UART_BUF_MASK (UART_BUF_SIZE - 1U)

typedef struct {
    uint8_t buffer[UART_BUF_SIZE];
    volatile uint32_t head;
    volatile uint32_t tail;
    volatile uint32_t overflow_count; // Лічильник подій переповнення
} uart_ring_buf_t;

// Запис із відкиданням нових байтів при переповненні (Drop New)
bool uart_ring_buf_put_drop(uart_ring_buf_t *rb, uint8_t byte) {
    uint32_t current_head = rb->head;
    uint32_t next_head = (current_head + 1U) & UART_BUF_MASK;

    if (next_head == rb->tail) {
        rb->overflow_count++; // Фіксація колізії без перезапису
        return false;
    }

    rb->buffer[current_head] = byte;
    __DMB(); // Бар'єр пам'яті: запис байта має передувати оновленню head
    rb->head = next_head;
    return true;
}

// Зчитування байта споживачем у фоновому циклі
bool uart_ring_buf_get(uart_ring_buf_t *rb, uint8_t *byte) {
    uint32_t current_tail = rb->tail;
    if (rb->head == current_tail) {
        return false; // Буфер порожній
    }

    *byte = rb->buffer[current_tail];
    __DMB(); // Бар'єр пам'яті: прочитати дані до оновлення вказівника tail
    rb->tail = (current_tail + 1U) & UART_BUF_MASK;
    return true;
}
