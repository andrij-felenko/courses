#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

typedef struct {
    uint64_t total_requests;
    uint64_t error_count;
    double processing_time_ms;
} metrics_data_t;

typedef struct {
    _Atomic uint32_t sequence;
    metrics_data_t data;
} seqlock_metrics_t;

// Небезпечний підхід: проведення обчислень усередині критичної секції
bool read_metrics_unsafe(seqlock_metrics_t *lock, double *avg_time) {
    uint32_t seq;
    metrics_data_t snapshot;
    do {
        seq = atomic_load_explicit(&lock->sequence, memory_order_acquire);
        if (seq & 1) continue; // Іде запис

        snapshot = lock->data; // Можливе розірване читання!
        
        // НЕБЕЗПЕКА: Ділення на розірване або нульове значення усередині циклу!
        // Якщо error_count прочитано некоректно або дорівнює total_requests
        *avg_time = snapshot.processing_time_ms / (snapshot.total_requests - snapshot.error_count);

    } while (atomic_load_explicit(&lock->sequence, memory_order_relaxed) != seq);
    return true;
}

// Безпечний підхід: тільки копіювання даних, обчислення винесені назовні
bool read_metrics_safe(const seqlock_metrics_t *lock, metrics_data_t *out_data) {
    uint32_t seq1, seq2;
    uint32_t attempts = 0;
    const uint32_t max_attempts = 1000;

    do {
        seq1 = atomic_load_explicit(&lock->sequence, memory_order_acquire);
        if (seq1 & 1) {
            attempts++;
            if (attempts > max_attempts) return false; // Захист від голодування
            continue;
        }

        // Копіюємо лише монолітний блок пам'яті без побічних ефектів
        memcpy(out_data, (const void*)&lock->data, sizeof(metrics_data_t));

        atomic_thread_fence(memory_order_acquire);
        seq2 = atomic_load_explicit(&lock->sequence, memory_order_relaxed);
    } while (seq1 != seq2);

    return true;
}
