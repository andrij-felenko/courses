#include <cmath>
#include <numbers>

struct Vector3 {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

[[nodiscard]] constexpr Vector3 enu_to_ned(const Vector3& enu) noexcept {
    return Vector3{
        .x =  enu.y,
        .y =  enu.x,
        .z = -enu.z
    };
}

[[nodiscard]] float yaw_enu_to_ned(float yaw_enu) noexcept {
    float yaw_ned = static_cast<float>(std::numbers::pi / 2.0) - yaw_enu;
    constexpr float two_pi = static_cast<float>(2.0 * std::numbers::pi);
    while (yaw_ned >  static_cast<float>(std::numbers::pi)) yaw_ned -= two_pi;
    while (yaw_ned < -static_cast<float>(std::numbers::pi)) yaw_ned += two_pi;
    return yaw_ned;
}
