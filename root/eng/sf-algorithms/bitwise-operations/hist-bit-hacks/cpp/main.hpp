#include <cstdint>
#include <bit>

[[nodiscard]] constexpr float fast_inv_sqrt(float number) noexcept {
    const float x2 = number * 0.5F;
    std::int32_t i = std::bit_cast<std::int32_t>(number);
    i = 0x5f3759df - (i >> 1U);
    float y = std::bit_cast<float>(i);
    y = y * (1.5F - (x2 * y * y));              // уточнення методом Ньютона
    return y;
}
