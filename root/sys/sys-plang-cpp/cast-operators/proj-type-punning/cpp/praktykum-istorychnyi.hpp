#include <bit>
#include <cstdint>

// Повністю стандарто-сумісна реалізація на C++20 (працює в constexpr!)
constexpr float fast_inverse_sqrt(float number) noexcept {
    const float x2 = number * 0.5f;
    const float threehalfs = 1.5f;

    // Безпечне побітове перенесення без порушення Strict Aliasing
    uint32_t i = std::bit_cast<uint32_t>(number);
    i = 0x5f3759dfu - (i >> 1);

    float y = std::bit_cast<float>(i);
    y = y * (threehalfs - (x2 * y * y)); // Метод Ньютона-Рафсона

    return y;
}

static_assert(fast_inverse_sqrt(4.0f) > 0.49f && fast_inverse_sqrt(4.0f) < 0.51f);
