#define SENSOR_QUEUE_SIZE 16U /* Розмір повинен бути ступенем двійки */

typedef struct {
    bmp280_sample_t buffer[SENSOR_QUEUE_SIZE];
    volatile uint32_t head; /* Індекс запису (змінюється тільки Producer ISR) */
    volatile uint32_t tail; /* Індекс читання (змінюється тільки Consumer Task) */
} sensor_spsc_queue_t;

static inline bool spsc_push(sensor_spsc_queue_t *q, const bmp280_sample_t *sample) {
    uint32_t current_head = q->head;
    uint32_t next_head = (current_head + 1U) & (SENSOR_QUEUE_SIZE - 1U);

    if (next_head == q->tail) {
        return false; /* Буфер переповнений (Overflow) */
    }

    q->buffer[current_head] = *sample;
    __DMB(); /* Data Memory Barrier: гарантує завершення запису даних до оновлення head */
    q->head = next_head;
    return true;
}

static inline bool spsc_pop(sensor_spsc_queue_t *q, bmp280_sample_t *out_sample) {
    uint32_t current_tail = q->tail;

    if (current_tail == q->head) {
        return false; /* Буфер порожній */
    }

    *out_sample = q->buffer[current_tail];
    __DMB(); /* Бар'єр пам'яті */
    q->tail = (current_tail + 1U) & (SENSOR_QUEUE_SIZE - 1U);
    return true;
}
