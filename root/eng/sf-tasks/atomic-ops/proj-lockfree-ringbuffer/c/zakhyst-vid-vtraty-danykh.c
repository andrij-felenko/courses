bool ring_push_with_stats(struct kernel_spsc_ring *rb, void *item, atomic_t *drops)
{
    int head = atomic_read(&rb->head);
    int tail = atomic_read_acquire(&rb->tail);

    if ((head - tail) >= RING_SIZE) {
        atomic_inc(drops); // Атомарно збільшуємо лічильник втрат
        return false;
    }

    rb->buffer[head & RING_MASK] = item;
    atomic_set_release(&rb->head, head + 1);
    return true;
}
