#include <cstdint>
#include <concepts>
#include <bit>

class BarrettReducer {
private:
    std::uint32_t modulus_;
    unsigned int k_;
    std::uint64_t mu_;

public:
    explicit constexpr BarrettReducer(std::uint32_t m) noexcept 
        : modulus_(m), k_(std::bit_width(m)), mu_((1ULL << (2 * std::bit_width(m))) / m) {}

    [[nodiscard]] constexpr std::uint32_t reduce(std::uint64_t x) const noexcept {
        const std::uint64_t q = ((x >> (k_ - 1)) * mu_) >> (k_ + 1);
        std::int64_t r = static_cast<std::int64_t>(x) - static_cast<std::int64_t>(q * modulus_);
        
        while (r >= modulus_) {
            r -= modulus_;
        }
        while (r < 0) {
            r += modulus_;
        }
        return static_cast<std::uint32_t>(r);
    }
};
