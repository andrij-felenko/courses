struct AtomicStats {
    long long request_count{0};
    long long error_count{0};
    constexpr AtomicStats() noexcept = default;
};

// Гарантована ініціалізація до запуску + повна можливість модифікації в процесі роботи:
constinit AtomicStats g_stats{};

void handle_request(bool ok) {
    g_stats.request_count++; // ПОВНІСТЮ ДОЗВОЛЕНО!
    if (!ok) g_stats.error_count++;
}
