#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>

typedef struct {
    double x;
    double y;
    double z;
    uint64_t timestamp_ns;
} position_state_t;

typedef struct {
    _Atomic uint32_t sequence;
    position_state_t state;
} seqlock_position_t;

void seqlock_position_init(seqlock_position_t *pos) {
    atomic_init(&pos->sequence, 0);
    pos->state = (position_state_t){0.0, 0.0, 0.0, 0};
}

// Письменник оновлює стан на місці без очікування читачів
void seqlock_position_write(seqlock_position_t *pos, double x, double y, double z, uint64_t ts) {
    uint32_t seq = atomic_load_explicit(&pos->sequence, memory_order_relaxed);
    
    // Переводимо лічильник у непарний стан (активний запис)
    atomic_store_explicit(&pos->sequence, seq + 1, memory_order_relaxed);
    atomic_thread_fence(memory_order_release);

    pos->state.x = x;
    pos->state.y = y;
    pos->state.z = z;
    pos->state.timestamp_ns = ts;

    // Фіксуємо парний стан (запис завершено)
    atomic_store_explicit(&pos->sequence, seq + 2, memory_order_release);
}
