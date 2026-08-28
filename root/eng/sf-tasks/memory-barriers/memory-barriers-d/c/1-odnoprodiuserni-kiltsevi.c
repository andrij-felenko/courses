// SPSC кільцевий буфер мовою C (ядро Linux)
void spsc_ring_enqueue(struct spsc_ring *ring, void *data)
{
    unsigned int head = ring->head;
    unsigned int tail = smp_load_acquire(&ring->tail);

    if ((head - tail) >= ring->size)
        return; // Буфер повністю заповнений

    ring->buffer[head & (ring->size - 1)] = data;
    smp_store_release(&ring->head, head + 1);
}

void *spsc_ring_dequeue(struct spsc_ring *ring)
{
    unsigned int tail = ring->tail;
    unsigned int head = smp_load_acquire(&ring->head);

    if (tail == head)
        return NULL; // Буфер порожній

    void *data = ring->buffer[tail & (ring->size - 1)];
    smp_store_release(&ring->tail, tail + 1);
    return data;
}
