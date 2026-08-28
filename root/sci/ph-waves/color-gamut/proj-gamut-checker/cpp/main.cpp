// C++20: Ідіоматичний Gamut Checker з використанням std::array, RAII та std::clamp
#include <iostream>
#include <array>
#include <algorithm>
#include <cmath>

namespace color {

struct Tristimulus {
    double x{0.0};
    double y{0.0};
    double z{0.0};
};

struct Chromaticity {
    double x{0.0};
    double y{0.0};
};

class ColorGamut {
public:
    using Matrix3x3 = std::array<std::array<double, 3>, 3>;

    static constexpr Matrix3x3 sRGB_Inverse_Matrix = {{
        {{ 3.2404542, -1.5371385, -0.4985314}},
        {{-0.9692660,  1.8760108,  0.0415560}},
        {{ 0.0556434, -0.2040259,  1.0572252}}
    }};

    explicit constexpr ColorGamut(
        Chromaticity r = {0.64, 0.33},
        Chromaticity g = {0.30, 0.60},
        Chromaticity b = {0.15, 0.06},
        Chromaticity w = {0.3127, 0.3290})
        : primary_r_(r), primary_g_(g), primary_b_(b), white_point_(w) {}

    [[nodiscard]] static constexpr Tristimulus to_linear_rgb(const Tristimulus& xyz) noexcept {
        const auto& m = sRGB_Inverse_Matrix;
        return Tristimulus{
            m[0][0]*xyz.x + m[0][1]*xyz.y + m[0][2]*xyz.z,
            m[1][0]*xyz.x + m[1][1]*xyz.y + m[1][2]*xyz.z,
            m[2][0]*xyz.x + m[2][1]*xyz.y + m[2][2]*xyz.z
        };
    }

    [[nodiscard]] static constexpr bool contains(const Tristimulus& xyz, double tolerance = 1e-6) noexcept {
        const auto rgb = to_linear_rgb(xyz);
        return (rgb.x >= -tolerance && rgb.x <= 1.0 + tolerance) &&
               (rgb.y >= -tolerance && rgb.y <= 1.0 + tolerance) &&
               (rgb.z >= -tolerance && rgb.z <= 1.0 + tolerance);
    }

    [[nodiscard]] static constexpr Tristimulus clip(const Tristimulus& xyz) noexcept {
        const auto rgb = to_linear_rgb(xyz);
        return Tristimulus{
            std::clamp(rgb.x, 0.0, 1.0),
            std::clamp(rgb.y, 0.0, 1.0),
            std::clamp(rgb.z, 0.0, 1.0)
        };
    }

private:
    Chromaticity primary_r_;
    Chromaticity primary_g_;
    Chromaticity primary_b_;
    Chromaticity white_point_;
};

} // namespace color

int main() {
    constexpr color::Tristimulus laser_light{0.14, 0.03, 0.85};
    constexpr bool in_gamut = color::ColorGamut::contains(laser_light);
    
    std::cout << "Contains in sRGB gamut: " << (in_gamut ? "true" : "false") << '\n';

    constexpr auto clipped = color::ColorGamut::clip(laser_light);
    std::cout << "Clipped Linear RGB: [" 
              << clipped.x << ", " 
              << clipped.y << ", " 
              << clipped.z << "]\n";
    return 0;
}
