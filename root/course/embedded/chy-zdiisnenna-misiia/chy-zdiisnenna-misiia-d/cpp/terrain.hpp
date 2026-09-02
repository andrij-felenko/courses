#pragma once

#include <cstddef>
#include <expected>
#include <optional>
#include <vector>

#include "mission.hpp"

namespace mission {

struct TerrainScan {
    float    min_clearance_m{0.0f};
    float    min_clearance_dist_m{0.0f};
    GeoPoint worst_point{};
    bool     collision{false};
};

// Підвікно рельєфу, вирізане з .HGT за охопленням місії.
class DemGrid {
public:
    DemGrid(GeoPoint south_west_origin, double cell_size_deg,
            std::size_t rows, std::size_t cols, float geoid_undulation_m);

    void set_elevation(std::size_t row, std::size_t col, float elevation_msl_m);

    // Білінійна інтерполяція між чотирма вузлами.
    // Порожній результат — точка поза підвікном: даних немає, і це відмова.
    [[nodiscard]] std::optional<float> sample_msl(double lat_deg, double lon_deg) const noexcept;

    // Приведення висоти GNSS (над еліпсоїдом WGS-84) до MSL моделі рельєфу.
    [[nodiscard]] float msl_from_ellipsoidal(float height_wgs84_m) const noexcept
    {
        return height_wgs84_m - geoid_undulation_m_;
    }

    [[nodiscard]] std::expected<TerrainScan, Failure> scan_leg(const GeoPoint& from,
                                                               const GeoPoint& to,
                                                               float step_m,
                                                               float safe_clearance_m) const;

    // Висота над землею — потрібна і вітру, і кліренсу.
    [[nodiscard]] std::optional<float> height_agl(const GeoPoint& point) const noexcept;

private:
    [[nodiscard]] float node(std::size_t row, std::size_t col) const noexcept
    {
        return nodes_[row * cols_ + col];
    }

    GeoPoint           origin_;
    double             cell_size_deg_;
    std::size_t        rows_;
    std::size_t        cols_;
    float              geoid_undulation_m_;
    std::vector<float> nodes_;
};

}  // namespace mission
