// Пакетне вилучення до 32 елементів за один атомарний крок
int ring_pop_batch(struct kernel_spsc_ring *rb, void **out_items, int max_items)
{
    int tail = atomic_read(&rb->tail);
    int head = atomic_read_acquire(&rb->head);
    int available = head - tail;

    if (available <= 0)
        return 0;

    int count = min(available, max_items);
    for (int i = 0; i < count; i++) {
        out_items[i] = rb->buffer[(tail + i) & RING_MASK];
    }

    atomic_set_release(&rb->tail, tail + count);
    return count;
}
