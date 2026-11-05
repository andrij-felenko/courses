#include <stdint.h>
#include <stdbool.h>

#define LOG_BUFFER_SIZE 1024
#define LOG_BUFFER_MASK (LOG_BUFFER_SIZE - 1)

typedef struct {
    uint8_t storage[LOG_BUFFER_SIZE];
    volatile uint32_t head;
    volatile uint32_t tail;
    volatile uint32_t dropped_events;
} binary_log_buffer_t;

static binary_log_buffer_t g_log_buffer;

/* Допоміжні функції керування глобальними перериваннями ядра */
static inline uint32_t disable_interrupts(void) {
    uint32_t state;
    __asm volatile ("mrs %0, primask\n cpsid i" : "=r" (state) :: "memory");
    return state;
}

static inline void restore_interrupts(uint32_t state) {
    __asm volatile ("msr primask, %0" :: "r" (state) : "memory");
}

/* Атомарне копіювання двійкового кадру в кільцевий буфер */
bool binary_log_write(uint16_t event_id, const uint8_t *payload, uint8_t payload_len) {
    const uint8_t total_len = sizeof(uint16_t) + sizeof(uint8_t) + payload_len;
    uint32_t state = disable_interrupts();

    uint32_t current_head = g_log_buffer.head;
    uint32_t current_tail = g_log_buffer.tail;
    uint32_t free_space = LOG_BUFFER_SIZE - (current_head - current_tail);

    if (free_space < total_len) {
        g_log_buffer.dropped_events++;
        restore_interrupts(state);
        return false;
    }

    g_log_buffer.head = current_head + total_len;
    restore_interrupts(state);

    /* Запис заголовка кадру */
    uint32_t write_idx = current_head & LOG_BUFFER_MASK;
    for (uint8_t i = 0; i < sizeof(uint16_t); ++i) {
        g_log_buffer.storage[(write_idx + i) & LOG_BUFFER_MASK] = (uint8_t)(event_id >> (i * 8));
    }
    write_idx = (write_idx + sizeof(uint16_t)) & LOG_BUFFER_MASK;

    /* Запис розміру корисного навантаження */
    g_log_buffer.storage[write_idx] = payload_len;
    write_idx = (write_idx + 1) & LOG_BUFFER_MASK;

    /* Копіювання двійкових аргументів */
    for (uint8_t i = 0; i < payload_len; ++i) {
        g_log_buffer.storage[(write_idx + i) & LOG_BUFFER_MASK] = payload[i];
    }

    return true;
}
