#include <cstdint>
#include <cstddef>
#include <span>
#include <vector>
#include <expected>
#include <string_view>

namespace Bignum {

using Limb = uint32_t;
using DoubleLimb = uint64_t;

enum class Status : int32_t {
    Ok                 =  0,
    NullPointer        = -1,
    BufferOverflow     = -2,
    InvalidLength      = -3,
    OutOfMemory        = -4
};

struct Config {
    size_t karatsubaThreshold = 32;
    size_t toom3Threshold     = 192;
};

/* Клас неволодіючого зрізу пам'яті для великого числа */
class BigIntSpan {
public:
    std::span<const Limb> data;

    constexpr explicit BigIntSpan(std::span<const Limb> view) noexcept : data(view) {}
    [[nodiscard]] size_t size() const noexcept { return data.size(); }
    [[nodiscard]] bool empty() const noexcept { return data.empty(); }
    [[nodiscard]] Limb operator[](size_t idx) const noexcept { return data[idx]; }
};

} // namespace Bignum
