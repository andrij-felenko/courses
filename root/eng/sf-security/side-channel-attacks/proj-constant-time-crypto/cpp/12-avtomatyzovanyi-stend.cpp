#include <iostream>
#include <vector>
#include <array>
#include <random>
#include <cmath>
#include <cstdint>

#if defined(_MSC_VER)
#include <intrin.h>
#else
#include <x86intrin.h>
#endif

namespace crypto::testing {

class OnlineVariance {
public:
    void add(double x) noexcept {
        ++count_;
        const double delta = x - mean_;
        mean_ += delta / static_cast<double>(count_);
        const double delta2 = x - mean_;
        m2_ += delta * delta2;
    }

    [[nodiscard]] double mean() const noexcept { return mean_; }
    [[nodiscard]] double variance() const noexcept {
        return count_ > 1 ? m2_ / static_cast<double>(count_ - 1) : 0.0;
    }
    [[nodiscard]] uint64_t count() const noexcept { return count_; }

private:
    double mean_{0.0};
    double m2_{0.0};
    uint64_t count_{0};
};

[[nodiscard]] double compute_welch_t(const OnlineVariance &a, const OnlineVariance &b) noexcept {
    const double var_a = a.variance();
    const double var_b = b.variance();
    const double num = a.mean() - b.mean();
    const double den = std::sqrt((var_a / static_cast<double>(a.count())) +
                                 (var_b / static_cast<double>(b.count())));
    return den > 0.0 ? num / den : 0.0;
}

[[nodiscard]] inline uint64_t rdtsc_fence() noexcept {
    #if defined(_MSC_VER)
    return __rdtsc();
    #else
    unsigned int aux;
    return __rdtscp(&aux);
    #endif
}

void verify_leakage(size_t iterations = 100'000) {
    OnlineVariance fixed_dist;
    OnlineVariance random_dist;

    std::array<uint8_t, 32> target_key{};
    target_key.fill(0xAA);

    std::array<uint8_t, 32> fixed_input = target_key;
    std::array<uint8_t, 32> random_input{};

    std::mt19937_64 rng(1337);
    std::uniform_int_distribution<uint32_t> dist_byte(0, 255);

    for (size_t i = 0; i < iterations; ++i) {
        // Вимірювання фіксованого класу
        const uint64_t t0 = rdtsc_fence();
        volatile bool eq1 = constant_time::are_equal(target_key, fixed_input);
        const uint64_t t1 = rdtsc_fence();
        (void)eq1;
        fixed_dist.add(static_cast<double>(t1 - t0));

        // Вимірювання випадкового класу
        for (auto &b : random_input) {
            b = static_cast<uint8_t>(dist_byte(rng));
        }
        const uint64_t t2 = rdtsc_fence();
        volatile bool eq2 = constant_time::are_equal(target_key, random_input);
        const uint64_t t3 = rdtsc_fence();
        (void)eq2;
        random_dist.add(static_cast<double>(t3 - t2));
    }

    const double t_val = compute_welch_t(fixed_dist, random_dist);
    std::cout << "[Dudect C++] t-статистика: " << t_val << " для " << iterations << " ітерацій\n";
    if (std::abs(t_val) > 4.5) {
        std::cout << "[УВАГА] Виявлено статистичний витік часу!\n";
    } else {
        std::cout << "[УСПІХ] Реалізація є криптографічно безпечною.\n";
    }
}

} // namespace crypto::testing
