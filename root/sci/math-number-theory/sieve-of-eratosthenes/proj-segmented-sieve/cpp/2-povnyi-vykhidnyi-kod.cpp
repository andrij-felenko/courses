// C++17 implementation: Modern RAII Cache-Aware Segmented Sieve
#include <iostream>
#include <vector>
#include <cmath>
#include <cstdint>
#include <algorithm>
#include <memory>

namespace math {

constexpr std::size_t L1_CACHE_BYTES = 32768; // 32 KB L1d cache target

class SegmentedSieve {
public:
    explicit SegmentedSieve(std::uint64_t n) : n_(n) {}

    [[nodiscard]] std::uint64_t countPrimes() const {
        if (n_ < 2) return 0;

        const auto limit = static_cast<std::uint32_t>(std::sqrt(n_));
        const auto basePrimes = generateBasePrimes(limit);
        
        std::uint64_t primeCount = basePrimes.size();

        // Буфер сегмента RAII
        std::vector<std::uint8_t> segment(L1_CACHE_BYTES, 1);

        for (std::uint64_t low = limit + 1; low <= n_; low += L1_CACHE_BYTES) {
            std::uint64_t high = std::min(low + L1_CACHE_BYTES - 1, n_);
            const std::size_t currentSegmentLen = high - low + 1;

            std::fill_n(segment.begin(), currentSegmentLen, 1);

            for (std::uint32_t p : basePrimes) {
                std::uint64_t start = ((low + p - 1) / p) * static_cast<std::uint64_t>(p);
                start = std::max(start, static_cast<std::uint64_t>(p) * p);

                for (std::uint64_t j = start; j <= high; j += p) {
                    segment[j - low] = 0;
                }
            }

            for (std::size_t i = 0; i < currentSegmentLen; ++i) {
                if (segment[i]) {
                    primeCount++;
                }
            }
        }

        return primeCount;
    }

private:
    std::uint64_t n_;

    [[nodiscard]] static std::vector<std::uint32_t> generateBasePrimes(std::uint32_t limit) {
        if (limit < 2) return {};

        std::vector<bool> isPrime(limit + 1, true);
        isPrime[0] = isPrime[1] = false;

        for (std::uint32_t p = 2; p * p <= limit; ++p) {
            if (isPrime[p]) {
                for (std::uint32_t i = p * p; i <= limit; i += p) {
                    isPrime[i] = false;
                }
            }
        }

        std::vector<std::uint32_t> primes;
        primes.reserve(limit / static_cast<std::size_t>(std::log(limit)));

        for (std::uint32_t i = 2; i <= limit; ++i) {
            if (isPrime[i]) {
                primes.push_back(i);
            }
        }
        return primes;
    }
};

} // namespace math

int main() {
    constexpr std::uint64_t N = 100'000'000; // 100 мільйонів
    std::cout << "C++17 Segmented Sieve for N = " << N << "...\n";
    
    math::SegmentedSieve sieve(N);
    std::uint64_t total = sieve.countPrimes();
    
    std::cout << "Загальна кількість простих чисел: " << total << '\n';
    return 0;
}
