#include <cstdint>

namespace bignum {

/* Обчислення n0' у compile-time або runtime */
constexpr uint64_t compute_n0_prime(uint64_t n0) noexcept {
    uint64_t inv = 1;
    for (int i = 0; i < 6; ++i) {
        inv = inv * (2 - n0 * inv);
    }
    return static_cast<uint64_t>(-static_cast<int64_t>(inv));
}

} // namespace bignum
