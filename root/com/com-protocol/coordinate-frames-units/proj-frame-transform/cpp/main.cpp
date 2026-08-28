#include <array>
#include <cmath>
#include <numbers>

namespace nav {

constexpr double WGS84_A = 6378137.0;
constexpr double WGS84_F = 1.0 / 298.257223563;
constexpr double WGS84_E2 = 2.0 * WGS84_F - WGS84_F * WGS84_F;

struct Vector3f {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] constexpr Vector3f cross(const Vector3f& o) const noexcept {
        return {
            y * o.z - z * o.y,
            z * o.x - x * o.z,
            x * o.y - y * o.x
        };
    }

    [[nodiscard]] constexpr float dot(const Vector3f& o) const noexcept {
        return x * o.x + y * o.y + z * o.z;
    }
};

struct GeodeticCoord {
    double lat_deg{0.0};
    double lon_deg{0.0};
    double alt_m{0.0};
};

struct Quaternion {
    float w{1.0f};
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] Quaternion normalized() const noexcept {
        const float norm_sq = w * w + x * x + y * y + z * z;
        if (norm_sq < 1e-12f) {
            return {1.0f, 0.0f, 0.0f, 0.0f};
        }
        const float inv_norm = 1.0f / std::sqrt(norm_sq);
        return {w * inv_norm, x * inv_norm, y * inv_norm, z * inv_norm};
    }

    [[nodiscard]] constexpr Vector3f rotate(const Vector3f& v) const noexcept {
        const Vector3f qv{x, y, z};
        const Vector3f t{
            2.0f * (qv.y * v.z - qv.z * v.y),
            2.0f * (qv.z * v.x - qv.x * v.z),
            2.0f * (qv.x * v.y - qv.y * v.x)
        };
        return {
            v.x + w * t.x + (qv.y * t.z - qv.z * t.y),
            v.y + w * t.y + (qv.z * t.x - qv.x * t.z),
            v.z + w * t.z + (qv.x * t.y - qv.y * t.x)
        };
    }
};

/* 1. Локальні декартові базиси NED <-> ENU */
[[nodiscard]] constexpr Vector3f ned_to_enu(const Vector3f& ned) noexcept {
    return {ned.y, ned.x, -ned.z};
}

[[nodiscard]] constexpr Vector3f enu_to_ned(const Vector3f& enu) noexcept {
    return {enu.y, enu.x, -enu.z};
}

/* 2. Зв'язані базиси корпусу Body FRD <-> Body FLU */
[[nodiscard]] constexpr Vector3f body_frd_to_flu(const Vector3f& frd) noexcept {
    return {frd.x, -frd.y, -frd.z};
}

[[nodiscard]] constexpr Vector3f body_flu_to_frd(const Vector3f& flu) noexcept {
    return {flu.x, -flu.y, -flu.z};
}

/* Нормалізація кута довготи */
[[nodiscard]] inline double normalize_angle(double rad) noexcept {
    return std::remainder(rad, 2.0 * std::numbers::pi);
}

/* 3. Проєкція геодезичних координат WGS84 у площину NED */
[[nodiscard]] inline Vector3f geodetic_to_ned(const GeodeticCoord& target, const GeodeticCoord& home) noexcept {
    constexpr double deg2rad = std::numbers::pi / 180.0;
    const double phi_0 = home.lat_deg * deg2rad;
    const double sin_phi = std::sin(phi_0);
    const double cos_phi = std::cos(phi_0);
    
    const double d_phi = (target.lat_deg - home.lat_deg) * deg2rad;
    const double d_lambda = normalize_angle((target.lon_deg - home.lon_deg) * deg2rad);

    const double denom = 1.0 - WGS84_E2 * sin_phi * sin_phi;
    const double sqrt_denom = std::sqrt(denom);
    const double m = (WGS84_A * (1.0 - WGS84_E2)) / (denom * sqrt_denom);
    const double n = WGS84_A / sqrt_denom;

    return {
        static_cast<float>(d_phi * (m + home.alt_m)),
        static_cast<float>(d_lambda * (n + home.alt_m) * cos_phi),
        static_cast<float>(-(target.alt_m - home.alt_m))
    };
}

} // namespace nav
