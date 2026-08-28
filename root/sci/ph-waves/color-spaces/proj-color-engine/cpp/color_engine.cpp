// color_engine.cpp - Ідіоматична реалізація мовою C++ (C++20)
#include <iostream>
#include <cmath>
#include <numbers>
#include <array>
#include <span>

namespace color {

struct RGB8 {
    uint8_t r{0};
    uint8_t g{0};
    uint8_t b{0};
};

struct RGBLinear {
    float r{0.0f};
    float g{0.0f};
    float b{0.0f};
};

struct XYZ {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

struct Oklab {
    float l{0.0f};
    float a{0.0f};
    float b{0.0f};
};

struct Oklch {
    float l{0.0f};
    float c{0.0f};
    float h{0.0f}; // у градусах [0..360]
};

class ColorConverter {
public:
    [[nodiscard]] static constexpr float srgb_to_linear(uint8_t val) noexcept {
        const float c = static_cast<float>(val) / 255.0f;
        if (c <= 0.04045f) {
            return c / 12.92f;
        }
        return std::pow((c + 0.055f) / 1.055f, 2.4f);
    }

    [[nodiscard]] static RGBLinear to_linear(RGB8 color) noexcept {
        return RGBLinear{
            .r = srgb_to_linear(color.r),
            .g = srgb_to_linear(color.g),
            .b = srgb_to_linear(color.b)
        };
    }

    [[nodiscard]] static XYZ to_xyz(RGBLinear lin) noexcept {
        return XYZ{
            .x = 0.4124564f * lin.r + 0.3575761f * lin.g + 0.1804375f * lin.b,
            .y = 0.2126729f * lin.r + 0.7151522f * lin.g + 0.0721750f * lin.b,
            .z = 0.0193339f * lin.r + 0.1191920f * lin.g + 0.9503041f * lin.b
        };
    }

    [[nodiscard]] static Oklab xyz_to_oklab(XYZ xyz) noexcept {
        const float l_c = 0.8189330101f * xyz.x + 0.3618667424f * xyz.y - 0.1288597137f * xyz.z;
        const float m_c = 0.0329845436f * xyz.x + 0.9293118715f * xyz.y + 0.0361456387f * xyz.z;
        const float s_c = 0.0482003018f * xyz.x + 0.2643662691f * xyz.y + 0.6338517070f * xyz.z;

        const float l_p = std::cbrt(l_c);
        const float m_p = std::cbrt(m_c);
        const float s_p = std::cbrt(s_c);

        return Oklab{
            .l = 0.2104542553f * l_p + 0.7936177850f * m_p - 0.0040720468f * s_p,
            .a = 1.9779984951f * l_p - 2.4285922050f * m_p + 0.4505937099f * s_p,
            .b = 0.0259040371f * l_p + 0.7827717662f * m_p - 0.8086758033f * s_p
        };
    }

    [[nodiscard]] static Oklab to_oklab(RGB8 color) noexcept {
        return xyz_to_oklab(to_xyz(to_linear(color)));
    }

    [[nodiscard]] static Oklch to_oklch(Oklab lab) noexcept {
        float h_deg = std::atan2(lab.b, lab.a) * (180.0f / std::numbers::pi_v<float>);
        if (h_deg < 0.0f) {
            h_deg += 360.0f;
        }
        return Oklch{
            .l = lab.l,
            .c = std::hypot(lab.a, lab.b),
            .h = h_deg
        };
    }

    [[nodiscard]] static float delta_e_ok(Oklab c1, Oklab c2) noexcept {
        return std::hypot(c1.l - c2.l, c1.a - c2.a, c1.b - c2.b);
    }
};

} // namespace color

int main() {
    constexpr color::RGB8 color1{.r = 255, .g = 0, .b = 0};
    constexpr color::RGB8 color2{.r = 200, .g = 20, .b = 10};

    const auto lab1 = color::ColorConverter::to_oklab(color1);
    const auto lab2 = color::ColorConverter::to_oklab(color2);

    const float de = color::ColorConverter::delta_e_ok(lab1, lab2);
    
    std::cout << "Oklab Color 1: L=" << lab1.l << ", a=" << lab1.a << ", b=" << lab1.b << "\n";
    std::cout << "Oklab Color 2: L=" << lab2.l << ", a=" << lab2.a << ", b=" << lab2.b << "\n";
    std::cout << "Delta E_OK = " << de << "\n";

    return 0;
}
