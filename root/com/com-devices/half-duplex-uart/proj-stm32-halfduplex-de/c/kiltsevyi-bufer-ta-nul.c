// Структура кільцевого буфера для прийому кадрів (C)
typedef struct {
    uint8_t storage[RS485_BUFFER_SIZE];
    volatile size_t head;
    volatile size_t tail;
} ring_buffer_t;

static inline bool ring_buffer_push(ring_buffer_t *rb, uint8_t byte) {
    size_t next = (rb->head + 1) % RS485_BUFFER_SIZE;
    if (next == rb->tail) {
        return false; // Переповнення буфера
    }
    rb->storage[rb->head] = byte;
    rb->head = next;
    return true;
}

static inline bool ring_buffer_pop(ring_buffer_t *rb, uint8_t *byte) {
    if (rb->head == rb->tail) {
        return false; // Буфер порожній
    }
    *byte = rb->storage[rb->tail];
    rb->tail = (rb->tail + 1) % RS485_BUFFER_SIZE;
    return true;
}
