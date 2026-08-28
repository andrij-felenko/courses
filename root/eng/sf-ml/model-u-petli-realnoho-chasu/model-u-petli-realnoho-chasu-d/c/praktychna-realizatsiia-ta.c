#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <string.h>

#define ML_OUTPUT_DIM 4

typedef struct {
    float values[ML_OUTPUT_DIM];
    uint64_t timestamp_us;
    uint32_t frame_id;
} ml_prediction_t;

typedef struct {
    ml_prediction_t buffers[3];
    atomic_uint_fast8_t clean_idx;
    uint8_t write_idx;
    uint8_t read_idx;
} lockfree_triple_buffer_t;

void triple_buffer_init(lockfree_triple_buffer_t *tb) {
    memset(tb->buffers, 0, sizeof(tb->buffers));
    atomic_init(&tb->clean_idx, 0);
    tb->write_idx = 1;
    tb->read_idx = 2;
}

/* Викликається виключно фоновим потоком ML (Producer) */
void triple_buffer_write(lockfree_triple_buffer_t *tb, const ml_prediction_t *data) {
    /* Запис даних у робочий буфер виробника */
    memcpy(&tb->buffers[tb->write_idx], data, sizeof(ml_prediction_t));
    
    /* Атомарна публікація з бар'єром Release: новий індекс стає clean, старий повертається у write */
    uint_fast8_t old_clean = atomic_exchange_explicit(&tb->clean_idx, tb->write_idx, memory_order_release);
    tb->write_idx = (uint8_t)old_clean;
}

/* Викликається виключно швидким контуром керування ISR (Consumer) */
bool triple_buffer_read(lockfree_triple_buffer_t *tb, ml_prediction_t *out_data) {
    /* Перевірка та захоплення свіжого буфера з бар'єром Acquire */
    uint_fast8_t current_clean = atomic_load_explicit(&tb->clean_idx, memory_order_acquire);
    
    if (current_clean != tb->read_idx) {
        /* Обмін індексами: читач забирає clean собі */
        uint_fast8_t old_clean = atomic_exchange_explicit(&tb->clean_idx, tb->read_idx, memory_order_acq_rel);
        tb->read_idx = (uint8_t)old_clean;
        
        memcpy(out_data, &tb->buffers[tb->read_idx], sizeof(ml_prediction_t));
        return true; /* Отримано новий свіжий кадр */
    }
    
    /* Нових кадрів немає: читач повторно бере поточний read-буфер */
    memcpy(out_data, &tb->buffers[tb->read_idx], sizeof(ml_prediction_t));
    return false; /* Дані старі (потрібна екстраполяція) */
}
