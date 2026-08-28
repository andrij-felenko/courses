// Продюсер (виклик з ISR). Повертає 1, якщо поклали; 0, якщо повно.
static inline int fifo_put(fifo_t *q, uint8_t byte)
{
    uint16_t h = q->head;
    uint16_t n = fifo_next(h);
    if (n == q->tail)          // повно → політика «відкинути новий»
        return 0;
    q->buf[h] = byte;          // 1) СПЕРШУ дані у слот
    q->head   = n;            // 2) ПОТІМ опублікувати нову голову
    return 1;
}

// Споживач (виклик з main/loop). Повертає 1 і байт у *out; 0, якщо порожньо.
static inline int fifo_get(fifo_t *q, uint8_t *out)
{
    uint16_t t = q->tail;
    if (t == q->head)          // порожньо
        return 0;
    *out    = q->buf[t];       // 1) СПЕРШУ прочитати дані
    q->tail = fifo_next(t);    // 2) ПОТІМ звільнити слот
    return 1;
}
