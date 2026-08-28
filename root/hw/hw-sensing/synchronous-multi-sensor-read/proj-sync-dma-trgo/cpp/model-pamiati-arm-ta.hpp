namespace concurrency {

template <typename T, std::size_t Capacity>
struct MemoryBarrierQueue {
    static void publish_frame(std::atomic<std::size_t>& head,
                              std::array<T, Capacity>& storage,
                              const T& item) noexcept {
        const auto current_head = head.load(std::memory_order_relaxed);
        storage[current_head] = item;

        // Встановлюємо бар'єр вивільнення пам'яті (Release Barrier)
        head.store((current_head + 1) % Capacity, std::memory_order_release);
    }
};

} // namespace concurrency
