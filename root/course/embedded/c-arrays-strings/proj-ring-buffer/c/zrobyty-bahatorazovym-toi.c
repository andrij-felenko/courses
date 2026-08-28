typedef struct {
    uint8_t  buf[RB_SIZE];
    volatile uint16_t head;
    volatile uint16_t tail;
} ring_t;

bool rb_put(ring_t *rb, uint8_t b) {
    uint16_t next = (rb->head + 1) & (RB_SIZE - 1);
    if (next == rb->tail) return false;
    rb->buf[rb->head] = b;
    rb->head = next;
    return true;
}
