#include <cstdint>

[[nodiscard]] constexpr int popcount_wegner(uint64_t x) noexcept {
    int count = 0;
    while (x != 0) {
        x &= (x - 1);
        ++count;
    }
    return count;
}
