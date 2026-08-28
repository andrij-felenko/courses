// Схема зчитування вибірок у user-space (C++20):
std::uint64_t head = std::atomic_load_explicit(
    reinterpret_cast<const std::atomic<std::uint64_t>*>(&hdr->data_head),
    std::memory_order_acquire
);
std::uint64_t tail = hdr->data_tail;

while (tail < head) {
    std::uint64_t offset = tail % data_size;
    auto* phead = reinterpret_cast<const struct perf_event_header*>(data_boundary + offset);
    
    // Обробка запису phead...
    tail += phead->size;
}

std::atomic_store_explicit(
    reinterpret_cast<std::atomic<std::uint64_t>*>(&hdr->data_tail),
    tail, std::memory_order_release
);
