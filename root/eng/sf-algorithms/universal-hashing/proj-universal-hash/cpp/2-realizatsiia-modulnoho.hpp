#include <cstdint>
#include <cstddef>
#include <concepts>
#include <span>
#include <random>
#include <stdexcept>

namespace universal_hashing {

constexpr uint64_t P61 = (1ULL << 61) - 1;

class ModularHasher {
public:
    ModularHasher(uint64_t m, uint64_t seed_a, uint64_t seed_b) : m_{m} {
        if (m == 0) throw std::invalid_argument("m must be > 0");
        a_ = (seed_a % (P61 - 1)) + 1;
        b_ = seed_b % P61;
    }

    [[nodiscard]] uint64_t operator()(uint64_t x) const noexcept {
        auto prod = static_cast<unsigned __int128>(a_) * x + b_;
        uint64_t sum = static_cast<uint64_t>(prod & P61) + static_cast<uint64_t>(prod >> 61);
        uint64_t rem = (sum >= P61) ? (sum - P61) : sum;
        return rem % m_;
    }

private:
    uint64_t a_;
    uint64_t b_;
    uint64_t m_;
};

class MultiplyShiftHasher {
public:
    MultiplyShiftHasher(uint32_t M, uint64_t seed_a) 
        : shift_{static_cast<uint32_t>(64 - M)}, mask_{(1ULL << M) - 1} {
        if (M == 0 || M >= 64) throw std::invalid_argument("Invalid M");
        a_ = seed_a | 1ULL;
    }

    [[nodiscard]] uint64_t operator()(uint64_t x) const noexcept {
        return (a_ * x) >> shift_;
    }

private:
    uint64_t a_;
    uint32_t shift_;
    uint64_t mask_;
};

} // namespace universal_hashing
