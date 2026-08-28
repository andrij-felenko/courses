#include <stdint.h>
#include <stdlib.h>

typedef struct {
    uint32_t base_delay_ms;
    uint32_t max_delay_ms;
    uint32_t current_delay_ms;
} retry_backoff_t;

void retry_backoff_init(retry_backoff_t *b, uint32_t base_ms, uint32_t max_ms) {
    b->base_delay_ms = base_ms;
    b->max_delay_ms = max_ms;
    b->current_delay_ms = base_ms;
}

uint32_t retry_backoff_next(retry_backoff_t *b, uint32_t random_seed) {
    /* Рівномірний псевдовипадковий коефіцієнт [0.0 .. 1.0] */
    uint32_t range = (b->current_delay_ms * 3u) - b->base_delay_ms;
    if (range == 0) range = 1;
    
    uint32_t jittered = b->base_delay_ms + (random_seed % range);
    if (jittered > b->max_delay_ms) {
        jittered = b->max_delay_ms;
    }
    b->current_delay_ms = jittered;
    return jittered;
}

uint32_t calculate_initial_jitter(uint32_t window_seconds, uint32_t random_val) {
    if (window_seconds == 0) return 0;
    return (random_val % window_seconds);
}
