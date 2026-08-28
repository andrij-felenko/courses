#include <iostream>
#include <vector>
#include <random>
#include <chrono>
#include <cstdint>
#include <bit>
#include <iomanip>
#include <pthread.h>

namespace bench {

template <typename T>
inline void do_not_optimize(T&& val) {
    #if defined(__clang__)
    asm volatile("" : "+r,m"(val) : : "memory");
    #else
    asm volatile("" : : "g"(val) : "memory");
    #endif
}

inline bool pin_to_core(int core_id) noexcept {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    return pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset) == 0;
}

} // namespace bench

// Метод 1: Наївний побітовий прохід
uint64_t popcount_naive(uint64_t x) noexcept {
    uint64_t count = 0;
    while (x) {
        count += (x & 1ULL);
        x >>= 1ULL;
    }
    return count;
}

// Метод 2: Стандартний C++20 std::popcount (апаратна інструкція POPCNT)
uint64_t popcount_std(uint64_t x) noexcept {
    return static_cast<uint64_t>(std::popcount(x));
}

template <typename Func>
double measure(Func&& fn, const std::vector<uint64_t>& data, std::size_t iters) {
    using clock = std::chrono::high_resolution_clock;

    // Фаза прогріву
    for (const auto val : data) {
        auto res = fn(val);
        bench::do_not_optimize(res);
    }

    const auto t0 = clock::now();
    for (std::size_t it = 0; it < iters; ++it) {
        for (const auto val : data) {
            auto res = fn(val);
            bench::do_not_optimize(res);
        }
    }
    const auto dt = std::chrono::duration_cast<std::chrono::nanoseconds>(clock::now() - t0);
    return static_cast<double>(dt.count()) / static_cast<double>(data.size() * iters);
}

int main() {
    bench::pin_to_core(0);

    constexpr std::size_t N = 1024;
    std::mt19937_64 rng(1337);
    std::vector<uint64_t> test_data(N);
    for (auto& item : test_data) {
        item = rng();
    }

    const double t_naive = measure(popcount_naive, test_data, 10000);
    const double t_std = measure(popcount_std, test_data, 10000);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "popcount_naive: " << t_naive << " нс / операція\n";
    std::cout << "popcount_std:   " << t_std << " нс / операція\n";
    std::cout << "Прискорення:    " << (t_naive / t_std) << "x\n";

    return 0;
}
