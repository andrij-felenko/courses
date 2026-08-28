/* Односпрямований неблокуючий кільцевий буфер (Single Producer Single Consumer) */
#define RING_BUFFER_SIZE 128

typedef struct {
    uint8_t buffer[RING_BUFFER_SIZE];
    volatile size_t head; /* Змінюється виробником (наприклад, ISR) */
    volatile size_t tail; /* Змінюється споживачем (фоновою задачею) */
} ring_buffer_t;

static inline bool ring_buffer_push(ring_buffer_t* rb, uint8_t byte) {
    size_t next_head = (rb->head + 1) % RING_BUFFER_SIZE;
    if (next_head == rb->tail) {
        return false; /* Переповнення буфера (Overflow) */
    }
    rb->buffer[rb->head] = byte;
    rb->head = next_head;
    return true;
}

static inline bool ring_buffer_pop(ring_buffer_t* rb, uint8_t* byte) {
    if (rb->head == rb->tail) {
        return false; /* Буфер порожній */
    }
    *byte = rb->buffer[rb->tail];
    rb->tail = (rb->tail + 1) % RING_BUFFER_SIZE;
    return true;
}
