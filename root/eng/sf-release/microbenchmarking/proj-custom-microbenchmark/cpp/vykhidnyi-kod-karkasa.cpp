#include <iostream>
#include <vector>
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <iomanip>
#include <thread>
#include <pthread.h>

namespace bench {

/* Оптимізаційний бар'єр для C++: гарантує обчислення виразу без накладних інструкцій */
template <typename T>
inline void do_not_optimize(T&& value) {
    #if defined(__clang__)
    asm volatile("" : "+r,m"(value) : : "memory");
    #else
    asm volatile("" : : "g"(value) : "memory");
    #endif
}

inline void clobber_memory() {
    asm volatile("" : : : "memory");
}

/* Прив'язка поточного потоку до конкретного процесорного ядра */
inline bool pin_current_thread(int core_id) noexcept {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    return pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset) == 0;
}

struct Statistics {
    double min_ns{0.0};
    double median_ns{0.0};
    double p95_ns{0.0};
    double p99_ns{0.0};
    double iqr_ns{0.0};
};

/* Розрахунок перцентиля за лінійною інтерполяцією для відсортованого вектора */
inline double percentile(const std::vector<double>& sorted, double p) noexcept {
    if (sorted.empty()) return 0.0;
    if (sorted.size() == 1) return sorted.front();
    const double k = p * static_cast<double>(sorted.size() - 1);
    const auto i = static_cast<std::size_t>(k);
    const double f = k - static_cast<double>(i);
    if (i >= sorted.size() - 1) return sorted.back();
    return sorted[i] + f * (sorted[i + 1] - sorted[i]);
}

/* Каркас прогону мікробенчмарку для довільного callable-об'єкта */
template <typename Func>
Statistics benchmark(Func&& fn, std::chrono::nanoseconds target_batch = std::chrono::milliseconds(2), std::size_t num_samples = 200) {
    using clock = std::chrono::high_resolution_clock;

    // 1. Автоматичне калібрування кількості ітерацій у батчі
    std::uint64_t iters = 16;
    while (true) {
        const auto t0 = clock::now();
        for (std::uint64_t i = 0; i < iters; ++i) {
            auto res = fn(i);
            do_not_optimize(res);
        }
        const auto dt = std::chrono::duration_cast<std::chrono::nanoseconds>(clock::now() - t0);
        if (dt >= target_batch || iters >= (1ULL << 30)) {
            break;
        }
        const auto dt_count = std::max<std::int64_t>(1, dt.count());
        iters = static_cast<std::uint64_t>((static_cast<double>(iters) * target_batch.count()) / dt_count) + 1;
    }

    // 2. Фаза прогріву (Warmup)
    for (std::uint64_t i = 0; i < iters; ++i) {
        auto res = fn(i);
        do_not_optimize(res);
    }

    // 3. Збір незалежних замірів
    std::vector<double> samples;
    samples.reserve(num_samples);

    for (std::size_t s = 0; s < num_samples; ++s) {
        const auto t0 = clock::now();
        for (std::uint64_t i = 0; i < iters; ++i) {
            auto res = fn(i);
            do_not_optimize(res);
        }
        const auto dt = std::chrono::duration_cast<std::chrono::nanoseconds>(clock::now() - t0);
        samples.push_back(static_cast<double>(dt.count()) / static_cast<double>(iters));
    }

    // 4. Статистичний аналіз
    std::sort(samples.begin(), samples.end());

    Statistics stats;
    stats.min_ns = samples.front();
    stats.median_ns = percentile(samples, 0.50);
    const double q1 = percentile(samples, 0.25);
    const double q3 = percentile(samples, 0.75);
    stats.iqr_ns = q3 - q1;
    stats.p95_ns = percentile(samples, 0.95);
    stats.p99_ns = percentile(samples, 0.99);

    return stats;
}

} // namespace bench

// Тестовий алгоритм: швидке 64-бітне псевдовипадкове перемішування
constexpr std::uint64_t hash_mix(std::uint64_t state) noexcept {
    std::uint64_t x = state + 0x9E3779B97F4A7C15ULL;
    x ^= (x >> 30);
    x *= 0xBF58476D1CE4E5B9ULL;
    x ^= (x >> 27);
    x *= 0x94D049BB133111EBULL;
    x ^= (x >> 31);
    return x;
}

int main() {
    if (bench::pin_current_thread(1)) {
        std::cout << "Потік успішно прив'язано до CPU 1\n";
    }

    std::cout << "Запуск мікробенчмарку hash_mix...\n";
    const auto stats = bench::benchmark(hash_mix, std::chrono::milliseconds(2), 200);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "--- Результати ---\n";
    std::cout << "Min:    " << stats.min_ns << " нс / операція\n";
    std::cout << "Median: " << stats.median_ns << " нс / операція\n";
    std::cout << "IQR:    " << stats.iqr_ns << " нс\n";
    std::cout << "p95:    " << stats.p95_ns << " нс\n";
    std::cout << "p99:    " << stats.p99_ns << " нс\n";

    return 0;
}
