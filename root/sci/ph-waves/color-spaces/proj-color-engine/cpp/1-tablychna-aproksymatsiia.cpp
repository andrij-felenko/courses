// C++ (C++20): Компіляція таблиці LUT на етапі компіляції через consteval / constexpr
#include <array>
#include <cmath>

namespace color {

[[nodiscard]] consteval std::array<float, 256> make_srgb_lut() noexcept {
    std::array<float, 256> lut{};
    for (size_t i = 0; i < 256; ++i) {
        const float c = static_cast<float>(i) / 255.0f;
        if (c <= 0.04045f) {
            lut[i] = c / 12.92f;
        } else {
            // C++20 constexpr math підтримка
            lut[i] = std::pow((c + 0.055f) / 1.055f, 2.4f);
        }
    }
    return lut;
}

inline constexpr auto srgb_lut = make_srgb_lut();

} // namespace color
