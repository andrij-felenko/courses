#include <stdbool.h>
#include <stdint.h>
#include <stdatomic.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define MAX_BACKOFF_LOOPS 64

typedef struct {
    _Atomic uint32_t value;
} atomic_counter_t;

void atomic_counter_init(atomic_counter_t *counter, uint32_t initial) {
    atomic_init(&counter->value, initial);
}

uint32_t atomic_counter_add_safe(atomic_counter_t *counter, uint32_t val) {
    uint32_t current = atomic_load_explicit(&counter->value, memory_order_relaxed);
    uint32_t desired;
    uint32_t backoff = 1;

    do {
        desired = current + val;
        // Використовуємо weak CAS для мінімізації накладних витрат на LL/SC
        if (atomic_compare_exchange_weak_explicit(&counter->value,
                                                  &current,
                                                  desired,
                                                  memory_order_release,
                                                  memory_order_relaxed)) {
            return desired;
        }
        
        // Апаратна затримка для зменшення колізій шини
        for (uint32_t i = 0; i < backoff; i++) {
            asm volatile("nop");
        }
        
        if (backoff < MAX_BACKOFF_LOOPS) {
            backoff <<= 1; // Експоненційне збільшення інтервалу
        }
    } while (true);
}
