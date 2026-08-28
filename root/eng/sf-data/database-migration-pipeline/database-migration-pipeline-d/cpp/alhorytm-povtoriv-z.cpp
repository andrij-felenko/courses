// Обчислення паузи перед повторною спробою захоплення блокування (C++)
#include <chrono>
#include <random>
#include <algorithm>

std::chrono::milliseconds calculate_backoff_delay(int attempt, 
                                                  std::chrono::milliseconds base, 
                                                  std::chrono::milliseconds max_delay) {
    auto factor = 1ULL << std::min(attempt, 30);
    auto raw_delay = std::min(base * factor, max_delay);

    static thread_local std::mt19937_64 rng(std::random_device{}());
    std::uniform_int_distribution<int64_t> dist(0, raw_delay.count() / 2);

    return raw_delay + std::chrono::milliseconds(dist(rng));
}
