// Запис у Lock-Free SPSC буфер без м'ютексів
bool spsc_push(const SecurityEvent& item) {
    const size_t current_tail = tail_.load(std::memory_order_relaxed);
    const size_t current_head = head_.load(std::memory_order_acquire);

    if ((current_tail + 1) % CAPACITY == current_head) {
        return false; // Буфер переповнений (протитиск)
    }

    buffer_[current_tail] = item;
    tail_.store((current_tail + 1) % CAPACITY, std::memory_order_release);
    return true;
}
