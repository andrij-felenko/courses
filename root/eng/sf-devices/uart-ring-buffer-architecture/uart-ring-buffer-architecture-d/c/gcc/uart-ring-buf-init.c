#include <stdint.h>
#include <stdbool.h>

#define UART_RING_BUF_SIZE 256U
#define UART_RING_BUF_MASK (UART_RING_BUF_SIZE - 1U)

typedef struct {
    uint8_t buffer[UART_RING_BUF_SIZE];
    volatile uint32_t head;
    volatile uint32_t tail;
} uart_ring_buf_t;

void uart_ring_buf_init(uart_ring_buf_t *ring) {
    ring->head = 0;
    ring->tail = 0;
}

bool uart_ring_buf_put(uart_ring_buf_t *ring, uint8_t data) {
    uint32_t current_head = ring->head;
    uint32_t next_head = (current_head + 1U) & UART_RING_BUF_MASK;
    
    // Перевірка на переповнення (Producer читає tail)
    if (next_head == ring->tail) {
        return false; // Буфер повний, новий байт відкидається
    }
    
    ring->buffer[current_head] = data;
    
    // Бар'єр пам'яті: запис даних у буфер завершується до публікації head
    __asm__ volatile ("dmb" ::: "memory");
    
    ring->head = next_head;
    return true;
}

bool uart_ring_buf_get(uart_ring_buf_t *ring, uint8_t *data) {
    uint32_t current_tail = ring->tail;
    
    // Consumer читає head
    if (current_tail == ring->head) {
        return false; // Буфер порожній
    }
    
    // Бар'єр пам'яті: читання head фіксується до вибірки даних із буфера
    __asm__ volatile ("dmb" ::: "memory");
    
    *data = ring->buffer[current_tail];
    ring->tail = (current_tail + 1U) & UART_RING_BUF_MASK;
    return true;
}
