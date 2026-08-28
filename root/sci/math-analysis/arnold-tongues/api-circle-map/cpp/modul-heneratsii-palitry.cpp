#include <cstdint>

namespace physics::nonlinear::api {

struct RGBColor {
    std::uint8_t r{0};
    std::uint8_t g{0};
    std::uint8_t b{0};
};

class ColorMapper {
public:
    [[nodiscard]] static constexpr RGBColor map_rotation(double w, bool is_locked) noexcept {
        if (is_locked) {
            return RGBColor{0, 128, 255};
        }
        const auto val = static_cast<std::uint8_t>(w * 255.0);
        return RGBColor{val, val, val};
    }
};

} // namespace physics::nonlinear::api
