#include <stdint.h>
#include <stdbool.h>
#include "driver/gpio.h"

#define DEBUG_GPIO_PIN GPIO_NUM_4
#define EMERGENCY_STOP_PIN GPIO_NUM_5

typedef struct {
    uint32_t isr_execution_count;
    uint32_t underrun_events;
    uint32_t max_isr_duration_ticks;
} dda_diagnostics_t;

static dda_diagnostics_t g_dda_diag = {0};

void dda_diagnostics_init(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << DEBUG_GPIO_PIN),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);
}

// Екстрена зупинка генератора кроків при виявленні збою
void IRAM_ATTR dda_emergency_stop(dda_ring_buffer_t *rb) {
    // Скидаємо буфер: прирівнюємо tail до head
    size_t h = atomic_load_explicit(&rb->head, memory_order_relaxed);
    atomic_store_explicit(&rb->tail, h, memory_order_relaxed);
    
    // Миттєво вимикаємо всі лінії STEP
    gpio_set_level(GPIO_NUM_19, 0);
    g_dda_diag.underrun_events++;
}

// Отримання поточної кількості елементів у буфері для запобігання underrun
size_t dda_queue_get_fill_level(const dda_ring_buffer_t *rb) {
    size_t h = atomic_load_explicit(&rb->head, memory_order_relaxed);
    size_t t = atomic_load_explicit(&rb->tail, memory_order_relaxed);
    if (h >= t) {
        return h - t;
    }
    return DDA_RING_BUFFER_SIZE - (t - h);
}
