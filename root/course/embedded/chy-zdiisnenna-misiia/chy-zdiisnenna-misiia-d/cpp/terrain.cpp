#include "terrain.hpp"

#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>

namespace mission {

DemGrid::DemGrid(GeoPoint south_west_origin, double cell_size_deg,
                 std::size_t rows, std::size_t cols, float geoid_undulation_m)
    : origin_(south_west_origin),
      cell_size_deg_(cell_size_deg),
      rows_(rows),
      cols_(cols),
      geoid_undulation_m_(geoid_undulation_m),
      nodes_(rows * cols, 0.0f)
{
    if (rows < 2 || cols < 2 || !(cell_size_deg > 0.0)) {
        throw std::invalid_argument("DemGrid: сітка менша за одну комірку");
    }
}

void DemGrid::set_elevation(std::size_t row, std::size_t col, float elevation_msl_m)
{
    if (row >= rows_ || col >= cols_) {
        throw std::out_of_range("DemGrid: вузол поза сіткою");
    }
    nodes_[row * cols_ + col] = elevation_msl_m;
}

std::optional<float> DemGrid::sample_msl(double lat_deg, double lon_deg) const noexcept
{
    const double gx = (lon_deg - origin_.longitude_deg) / cell_size_deg_;
    const double gy = (lat_deg - origin_.latitude_deg) / cell_size_deg_;

    if (!(gx >= 0.0) || !(gy >= 0.0) ||
        gx > static_cast<double>(cols_ - 1) || gy > static_cast<double>(rows_ - 1)) {
        return std::nullopt;
    }

    // Точка рівно на верхній межі належить останній повній комірці.
    const auto ix = std::min(static_cast<std::size_t>(std::floor(gx)), cols_ - 2);
    const auto iy = std::min(static_cast<std::size_t>(std::floor(gy)), rows_ - 2);

    const auto fx = static_cast<float>(gx - static_cast<double>(ix));
    const auto fy = static_cast<float>(gy - static_cast<double>(iy));

    const float top = std::lerp(node(iy, ix), node(iy, ix + 1), fx);
    const float bot = std::lerp(node(iy + 1, ix), node(iy + 1, ix + 1), fx);
    return std::lerp(top, bot, fy);
}

std::optional<float> DemGrid::height_agl(const GeoPoint& point) const noexcept
{
    const auto terrain = sample_msl(point.latitude_deg, point.longitude_deg);
    if (!terrain) {
        return std::nullopt;
    }
    return point.altitude_msl_m - *terrain;
}

std::expected<TerrainScan, Failure> DemGrid::scan_leg(const GeoPoint& from,
                                                      const GeoPoint& to,
                                                      float step_m,
                                                      float safe_clearance_m) const
{
    const float leg_dist = distance_m(from, to);
    step_m = std::max(step_m, 1.0f);

    // Крок беруть не більшим за половину комірки DEM, інакше пагорб між
    // двома пробами лишається непоміченим.
    const auto steps = std::max<std::size_t>(1, static_cast<std::size_t>(std::ceil(leg_dist / step_m)));

    TerrainScan scan;
    scan.min_clearance_m = std::numeric_limits<float>::max();
    scan.worst_point     = from;

    for (std::size_t s = 0; s <= steps; ++s) {
        const float    t     = static_cast<float>(s) / static_cast<float>(steps);
        const GeoPoint point = interpolate(from, to, t);

        const auto terrain = sample_msl(point.latitude_deg, point.longitude_deg);
        if (!terrain) {
            return std::unexpected(Failure::DemGap);
        }

        const float clearance = point.altitude_msl_m - *terrain;
        if (clearance < scan.min_clearance_m) {
            scan.min_clearance_m      = clearance;
            scan.min_clearance_dist_m = leg_dist * t;
            scan.worst_point          = point;
        }
        if (clearance < safe_clearance_m) {
            scan.collision = true;
            return scan;   // точку колізії знайдено, далі рахувати нема сенсу
        }
    }
    return scan;
}

}  // namespace mission
