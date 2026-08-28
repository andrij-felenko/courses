enum class DedupPolicy : uint8_t {
    HashSet, // Дедуплікація через std::unordered_set O(1)
    Bloom,   // Ймовірнісна дедуплікація через фільтр Блума
    Array    // Лінійний пошук O(N) у масиві (для малих систем)
};

struct DovetailConfig {
    std::size_t initial_task_capacity{64};
    std::size_t initial_result_capacity{256};
    std::size_t memory_limit_bytes{0}; // 0 = без обмежень
    std::uint64_t max_diagonals{0};      // 0 = нескінченно
    DedupPolicy dedup_policy{DedupPolicy::HashSet};
    bool enable_profiling{false};
};
