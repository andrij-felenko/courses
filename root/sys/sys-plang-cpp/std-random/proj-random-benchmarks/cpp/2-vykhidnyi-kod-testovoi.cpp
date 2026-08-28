#include <iostream>
#include <random>
#include <vector>
#include <chrono>
#include <cmath>
#include <numeric>
#include <iomanip>

// Компактна реалізація PCG32 для порівняння з mt19937
class pcg32_engine {
public:
    using result_type = uint32_t;

    explicit pcg32_engine(uint64_t seed = 0x853c49e6748fea9bULL, uint64_t seq = 0xda3e39cb9edb9d2dULL)
        : state_(0U), inc_((seq << 1u) | 1u) {
        step();
        state_ += seed;
        step();
    }

    static constexpr result_type min() { return 0; }
    static constexpr result_type max() { return std::numeric_limits<uint32_t>::max(); }

    result_type operator()() {
        uint64_t oldstate = state_;
        step();
        uint32_t xorshifted = static_cast<uint32_t>(((oldstate >> 18u) ^ oldstate) >> 27u);
        uint32_t rot = static_cast<uint32_t>(oldstate >> 59u);
        return (xorshifted >> rot) | (xorshifted << ((-rot) & 31));
    }

private:
    void step() {
        state_ = state_ * 6364136223846793005ULL + inc_;
    }

    uint64_t state_;
    uint64_t inc_;
};

// Шаблонована функція вимірювання швидкодії генератора
template<typename Engine>
void benchmark_engine(const std::string& name, size_t iterations) {
    Engine rng(1337);
    typename Engine::result_type dummy = 0;

    auto t1 = std::chrono::high_resolution_clock::now();
    for (size_t i = 0; i < iterations; ++i) {
        dummy += rng();
    }
    auto t2 = std::chrono::high_resolution_clock::now();

    double seconds = std::chrono::duration<double>(t2 - t1).count();
    double mops = (iterations / seconds) / 1e6;

    std::cout << std::left << std::setw(28) << name 
              << ": " << std::right << std::setw(8) << std::fixed << std::setprecision(2) 
              << mops << " MOps/s (Checksum: " << dummy << ")\n";
}

// Статистичний критерій згоди Хі-квадрат (Chi-Square Test)
template<typename Engine>
void test_chi_square(const std::string& name, size_t samples, size_t num_buckets) {
    Engine rng(42);
    std::uniform_int_distribution<size_t> dist(0, num_buckets - 1);
    std::vector<size_t> buckets(num_buckets, 0);

    for (size_t i = 0; i < samples; ++i) {
        buckets[dist(rng)]++;
    }

    double expected = static_cast<double>(samples) / num_buckets;
    double chi_square = 0.0;

    for (size_t count : buckets) {
        double diff = count - expected;
        chi_square += (diff * diff) / expected;
    }

    std::cout << "  Chi-Square (" << name << "): " << chi_square 
              << " (Очікуване значення при d.o.f=" << (num_buckets - 1) << " дорівнює ~" << (num_buckets - 1) << ")\n";
}

int main() {
    constexpr size_t N = 100000000;
    std::cout << "=========================================================\n";
    std::cout << "   БЕНЧМАРК ШВИДКОДІЇ ГЕНЕРАТОРІВ (100 млн вибірок)\n";
    std::cout << "=========================================================\n";

    benchmark_engine<std::minstd_rand>("std::minstd_rand (LCG)", N);
    benchmark_engine<std::mt19937>("std::mt19937 (MT32)", N);
    benchmark_engine<std::mt19937_64>("std::mt19937_64 (MT64)", N);
    benchmark_engine<pcg32_engine>("pcg32_engine (PCG)", N);

    std::cout << "\n=========================================================\n";
    std::cout << "   СТАТИСТИЧНИЙ ТЕСТ РІВНОМІРНОСТІ (Хі-квадрат Пірсона)\n";
    std::cout << "=========================================================\n";

    test_chi_square<std::mt19937>("std::mt19937", 1000000, 100);
    test_chi_square<pcg32_engine>("pcg32_engine", 1000000, 100);

    return 0;
}
