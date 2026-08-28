// geofence_engine.hpp — Сучасний C++20 модуль геозонування.
// Використовує строгу типізацію, constexpr та std::span.

#pragma once
#include <cstdint>
#include <span>
#include <array>
#include <cmath>
#include <numbers>

namespace drone::geofence {

struct GeoPoint {
    std::int32_t lat_e7{0};
    std::int32_t lon_e7{0};
    float        alt_m{0.0f};
};

struct VelocityNed {
    float vx{0.0f};
    float vy{0.0f};
    float vz{0.0f};

    [[nodiscard]] float speed() const noexcept {
        return std::sqrt(vx * vx + vy * vy + vz * vz);
    }
};

struct BoundingBoxAABB {
    std::int32_t min_lat{0};
    std::int32_t max_lat{0};
    std::int32_t min_lon{0};
    std::int32_t max_lon{0};

    [[nodiscard]] constexpr bool contains(std::int32_t lat, std::int32_t lon) const noexcept {
        return lat >= min_lat && lat <= max_lat && lon >= min_lon && lon <= max_lon;
    }
};

enum class ZoneType : std::uint8_t {
    KeepIn,
    KeepOut
};

inline constexpr std::size_t MaxPolygonVertices = 16;
inline constexpr std::size_t MaxPolygons        = 8;
inline constexpr std::size_t MaxCylinders       = 8;

struct PolygonFence {
    std::array<GeoPoint, MaxPolygonVertices> vertices{};
    std::uint8_t                            count{0};
    ZoneType                                type{ZoneType::KeepIn};
    float                                   alt_min{0.0f};
    float                                   alt_max{120.0f};
    BoundingBoxAABB                         aabb{};
    bool                                    active{true};

    void update_aabb() noexcept {
        if (count == 0) return;
        aabb.min_lat = aabb.max_lat = vertices[0].lat_e7;
        aabb.min_lon = aabb.max_lon = vertices[0].lon_e7;

        for (std::size_t i = 1; i < count; ++i) {
            aabb.min_lat = std::min(aabb.min_lat, vertices[i].lat_e7);
            aabb.max_lat = std::max(aabb.max_lat, vertices[i].lat_e7);
            aabb.min_lon = std::min(aabb.min_lon, vertices[i].lon_e7);
            aabb.max_lon = std::max(aabb.max_lon, vertices[i].lon_e7);
        }
    }
};

struct CylinderFence {
    GeoPoint center{};
    float    radius_m{100.0f};
    float    alt_min{0.0f};
    float    alt_max{120.0f};
    ZoneType type{ZoneType::KeepIn};
    bool     active{true};
};

class GeofenceEngine {
public:
    struct Config {
        float max_braking_accel_mps2{2.5f};
        float system_latency_s{0.3f};
        float static_margin_m{5.0f};
    };

    explicit constexpr GeofenceEngine(Config cfg = {}) noexcept : config_{cfg} {}

    [[nodiscard]] bool check_containment(const GeoPoint& p) const noexcept {
        bool has_keep_in = false;
        bool inside_keep_in = false;

        // Перевірка полігональних зон
        for (std::size_t i = 0; i < poly_count_; ++i) {
            const auto& poly = polygons_[i];
            if (!poly.active) continue;

            const bool alt_ok = (p.alt_m >= poly.alt_min && p.alt_m <= poly.alt_max);
            const bool in_poly = alt_ok && is_inside_polygon(p.lat_e7, p.lon_e7, poly);

            if (poly.type == ZoneType::KeepIn) {
                has_keep_in = true;
                if (in_poly) inside_keep_in = true;
            } else {
                if (in_poly) return false; // Порушення Keep-Out
            }
        }

        // Перевірка циліндричних зон
        for (std::size_t i = 0; i < cyl_count_; ++i) {
            const auto& cyl = cylinders_[i];
            if (!cyl.active) continue;

            const bool in_cyl = is_inside_cylinder(p, cyl);
            if (cyl.type == ZoneType::KeepIn) {
                has_keep_in = true;
                if (in_cyl) inside_keep_in = true;
            } else {
                if (in_cyl) return false; // Порушення Keep-Out
            }
        }

        return !has_keep_in || inside_keep_in;
    }

    [[nodiscard]] bool predict_breach(const GeoPoint& p, const VelocityNed& vel) const noexcept {
        if (!check_containment(p)) return false;

        const float spd = vel.speed();
        if (spd < 0.1f) return true;

        const float d_stop = spd * config_.system_latency_s +
                             (spd * spd) / (2.0f * config_.max_braking_accel_mps2) +
                             config_.static_margin_m;

        const float dt = d_stop / spd;
        const float d_north = vel.vx * dt;
        const float d_east  = vel.vy * dt;
        const float d_alt   = vel.vz * dt;

        GeoPoint p_pred;
        p_pred.lat_e7 = p.lat_e7 + static_cast<std::int32_t>(d_north * (1e7f / 111319.5f));
        const float lat_rad = static_cast<float>(p.lat_e7) * 1e-7f * (std::numbers::pi_v<float> / 180.0f);
        p_pred.lon_e7 = p.lon_e7 + static_cast<std::int32_t>(d_east * (1e7f / (111319.5f * std::cos(lat_rad))));
        p_pred.alt_m  = p.alt_m + d_alt;

        return check_containment(p_pred);
    }

    bool add_polygon(PolygonFence poly) noexcept {
        if (poly_count_ >= MaxPolygons) return false;
        poly.update_aabb();
        polygons_[poly_count_++] = poly;
        return true;
    }

    bool add_cylinder(const CylinderFence& cyl) noexcept {
        if (cyl_count_ >= MaxCylinders) return false;
        cylinders_[cyl_count_++] = cyl;
        return true;
    }

private:
    [[nodiscard]] static bool is_inside_polygon(std::int32_t lat, std::int32_t lon,
                                                const PolygonFence& poly) noexcept {
        if (!poly.aabb.contains(lat, lon)) return false;

        bool inside = false;
        std::size_t j = poly.count - 1;

        for (std::size_t i = 0; i < poly.count; ++i) {
            const std::int32_t yi = poly.vertices[i].lat_e7;
            const std::int32_t xi = poly.vertices[i].lon_e7;
            const std::int32_t yj = poly.vertices[j].lat_e7;
            const std::int32_t xj = poly.vertices[j].lon_e7;

            if ((yi <= lat && lat < yj) || (yj <= lat && lat < yi)) {
                const std::int64_t cross = static_cast<std::int64_t>(lon - xi) * (yj - yi) -
                                           static_cast<std::int64_t>(lat - yi) * (xj - xi);

                if (yi < yj) {
                    if (cross < 0) inside = !inside;
                } else {
                    if (cross > 0) inside = !inside;
                }
            }
            j = i;
        }
        return inside;
    }

    [[nodiscard]] static bool is_inside_cylinder(const GeoPoint& p,
                                                 const CylinderFence& cyl) noexcept {
        if (p.alt_m < cyl.alt_min || p.alt_m > cyl.alt_max) return false;

        const float lat_rad = static_cast<float>(cyl.center.lat_e7) * 1e-7f * (std::numbers::pi_v<float> / 180.0f);
        const float d_lat_m = static_cast<float>(p.lat_e7 - cyl.center.lat_e7) * 1e-7f * 111319.5f;
        const float d_lon_m = static_cast<float>(p.lon_e7 - cyl.center.lon_e7) * 1e-7f * 111319.5f * std::cos(lat_rad);

        return (d_lat_m * d_lat_m + d_lon_m * d_lon_m) <= (cyl.radius_m * cyl.radius_m);
    }

    Config                                      config_{};
    std::array<PolygonFence, MaxPolygons>       polygons_{};
    std::array<CylinderFence, MaxCylinders>     cylinders_{};
    std::size_t                                 poly_count_{0};
    std::size_t                                 cyl_count_{0};
};

} // namespace drone::geofence
