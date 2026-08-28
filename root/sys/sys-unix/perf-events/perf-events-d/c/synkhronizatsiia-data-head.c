// Схема зчитування вибірок у user-space (C):
uint64_t head = atomic_load_explicit((_Atomic uint64_t *)&hdr->data_head, memory_order_acquire);
uint64_t tail = hdr->data_tail;

while (tail < head) {
    uint64_t offset = tail % data_size;
    struct perf_event_header *phead = (void *)(data_boundary + offset);
    
    // Обробка запису phead...
    tail += phead->size;
}

atomic_store_explicit((_Atomic uint64_t *)&hdr->data_tail, tail, memory_order_release);
