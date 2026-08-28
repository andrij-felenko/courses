#include <cstdint>
#include <cmath>
#include <random>

// Емпірична BER для BPSK за одного Eb/N0 — тісний цикл, пам'ять O(1).
// Крутить біти по одному, доки не збере target_errors помилок.
struct Result { double ber; uint64_t errors, total; };

Result simulate_ber(double ebn0_db,
                    uint64_t target_errors = 200,
                    uint64_t max_bits = 100'000'000'000ULL,
                    uint64_t seed = 2024) {
    const double g     = std::pow(10.0, ebn0_db / 10.0);  // Eb/N0 у рази
    const double sigma = 1.0 / std::sqrt(2.0 * g);        // σ² = N0/2 = 1/(2γ)

    std::mt19937_64 gen(seed);
    std::bernoulli_distribution src(0.5);                 // джерело бітів
    std::normal_distribution<double> noise(0.0, sigma);   // шум AWGN

    uint64_t errors = 0, total = 0;
    while (errors < target_errors && total < max_bits) {
        int    bit = src(gen);              // 0 або 1
        double s   = 2 * bit - 1;           // BPSK: 0→−1, 1→+1
        double r   = s + noise(gen);        // + шум
        int    dec = (r > 0.0) ? 1 : 0;     // поріг у нулі
        errors += (dec != bit);             // лічимо розбіжність
        ++total;
    }
    return { double(errors) / total, errors, total };
}
