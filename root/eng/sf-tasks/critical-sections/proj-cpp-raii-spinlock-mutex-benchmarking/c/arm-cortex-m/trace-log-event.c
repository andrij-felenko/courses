#include <stdint.h>
#include "stm32f4xx.h"

#define TRACE_BUF_SIZE 64

typedef struct {
    uint32_t timestamp;
    uint32_t thread_id;
    uint8_t  event_type; // 1 = Enter, 2 = Exit, 3 = Timeout
} trace_record_t;

typedef struct {
    trace_record_t buffer[TRACE_BUF_SIZE];
    volatile uint32_t head;
} trace_ring_buffer_t;

static trace_ring_buffer_t g_trace_log;

void trace_log_event(uint32_t thread_id, uint8_t event_type) {
    uint32_t idx = g_trace_log.head % TRACE_BUF_SIZE;
    g_trace_log.buffer[idx].timestamp = DWT->CYCCNT;
    g_trace_log.buffer[idx].thread_id = thread_id;
    g_trace_log.buffer[idx].event_type = event_type;
    g_trace_log.head++;
}

int safe_spinlock_acquire(volatile uint32_t *lock, uint32_t thread_id, uint32_t max_wait_cycles) {
    uint32_t start_time = DWT->CYCCNT;
    trace_log_event(thread_id, 1);
    
    while (__LDREXW(lock) != 0 || __STREXW(1, lock) != 0) {
        if ((DWT->CYCCNT - start_time) > max_wait_cycles) {
            trace_log_event(thread_id, 3); // Фіксація таймауту
            return 0; // Помилка: перевищено тайм-аут очікування
        }
        __NOP();
    }
    __DMB();
    return 1; // Захоплення успішне
}
