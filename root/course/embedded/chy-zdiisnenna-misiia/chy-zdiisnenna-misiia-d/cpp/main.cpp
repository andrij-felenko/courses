#include <cmath>
#include <vector>
#include <span>
#include <optional>
#include <expected>
#include <numbers>
#include <algorithm>

enum class FeasibilityError {
    EmptyMission,
    WindUnfeasible,
    TerrainCollision,
    ClimbRateExceeded,
    InsufficientEnergy,
    TimeWindowExceeded
};

struct GeoCoordinate {
    double latitude_deg{0.0};
    double longitude_deg{0.0};
    float  altitude_msl_m{0.0f};
};

struct Waypoint {
    GeoCoordinate position;
    float airspeed_mps{15.0f};
    float loiter_time_s{0.0f};
};

struct WindVector {
    float speed_mps{0.0f};
    float direction_deg{0.0f}; // Напрямок, звідки дме вітер
};

struct DronePerformanceModel {
    float mass_kg{2.5f};
    float max_climb_rate_mps{4.0f};
    float hover_power_watts{180.0f};
    float avionics_power_watts{25.0f};
    float battery_capacity_wh{150.0f};
    float reserve_margin{0.25f}; // 25% резерву
};

class DemElevationGrid {
public:
    static constexpr size_t GridSize = 32;

    DemElevationGrid(GeoCoordinate origin, double cell_size_deg)
        : origin_(origin), cell_size_deg_(cell_size_deg) {
        elevations_.resize(GridSize * GridSize, 0.0f);
    }

    void set_elevation(size_t x, size_t y, float alt_m) {
        if (x < GridSize && y < GridSize) {
            elevations_[y * GridSize + x] = alt_m;
        }
    }

    [[nodiscard]] float sample_altitude(double lat, double lon) const noexcept {
        const double gx = (lon - origin_.longitude_deg) / cell_size_deg_;
        const double gy = (lat - origin_.latitude_deg) / cell_size_deg_;

        if (gx < 0.0 || gx >= GridSize - 1 || gy < 0.0 || gy >= GridSize - 1) {
            return 0.0f;
        }

        const auto ix = static_cast<size_t>(gx);
        const auto iy = static_cast<size_t>(gy);
        const auto fx = static_cast<float>(gx - ix);
        const auto fy = static_cast<float>(gy - iy);

        const float h00 = elevations_[iy * GridSize + ix];
        const float h10 = elevations_[iy * GridSize + (ix + 1)];
        const float h01 = elevations_[(iy + 1) * GridSize + ix];
        const float h11 = elevations_[(iy + 1) * GridSize + (ix + 1)];

        const float top = std::lerp(h00, h10, fx);
        const float bot = std::lerp(h01, h11, fx);
        return std::lerp(top, bot, fy);
    }

private:
    GeoCoordinate origin_;
    double cell_size_deg_{0.001};
    std::vector<float> elevations_;
};

struct MissionFeasibilityReport {
    float total_distance_m{0.0f};
    float total_time_s{0.0f};
    float total_energy_wh{0.0f};
    float min_terrain_clearance_m{9999.0f};
    float remaining_battery_pct{100.0f};
};

class MissionFeasibilityValidator {
public:
    static constexpr float MetersPerDegree = 111320.0f;
    static constexpr float MinSafeGroundSpeedMps = 3.0f;

    static std::expected<MissionFeasibilityReport, FeasibilityError>
    validate(std::span<const Waypoint> waypoints,
             const WindVector& wind,
             const DemElevationGrid& dem,
             const DronePerformanceModel& drone,
             float min_clearance_m = 40.0f,
             float max_time_s = 3600.0f) {

        if (waypoints.size() < 2) {
            return std::unexpected(FeasibilityError::EmptyMission);
        }

        MissionFeasibilityReport report;
        float total_energy_joules = 0.0f;

        for (size_t i = 0; i < waypoints.size() - 1; ++i) {
            const auto& w1 = waypoints[i];
            const auto& w2 = waypoints[i + 1];

            // Розрахунок геодезичного відрізка
            const auto [leg_dist, leg_bearing] = calc_distance_bearing(w1.position, w2.position);
            report.total_distance_m += leg_dist;

            // 1. Вітровий трикутник
            const float v_air = w2.airspeed_mps;
            const float wind_rad = (wind.direction_deg - leg_bearing) * (std::numbers::pi_v<float> / 180.0f);
            const float w_parallel = -wind.speed_mps * std::cos(wind_rad);
            const float w_perp     =  wind.speed_mps * std::sin(wind_rad);

            if (std::abs(w_perp) >= v_air) {
                return std::unexpected(FeasibilityError::WindUnfeasible);
            }

            const float sin_beta = w_perp / v_air;
            const float cos_beta = std::sqrt(1.0f - sin_beta * sin_beta);
            const float v_ground = v_air * cos_beta + w_parallel;

            if (v_ground < MinSafeGroundSpeedMps) {
                return std::unexpected(FeasibilityError::WindUnfeasible);
            }

            const float leg_time = leg_dist / v_ground;
            report.total_time_s += leg_time;

            // 2. Вертикальний профіль
            const float delta_h = w2.position.altitude_msl_m - w1.position.altitude_msl_m;
            const float climb_rate = delta_h / leg_time;
            if (climb_rate > drone.max_climb_rate_mps) {
                return std::unexpected(FeasibilityError::ClimbRateExceeded);
            }

            // 3. Дискретизація рельєфу (крок 20 метрів)
            constexpr float SampleStepM = 20.0f;
            const auto steps = std::max(size_t{1}, static_cast<size_t>(leg_dist / SampleStepM));

            for (size_t s = 0; s <= steps; ++s) {
                const float alpha = static_cast<float>(s) / static_cast<float>(steps);
                const double cur_lat = std::lerp(w1.position.latitude_deg, w2.position.latitude_deg, alpha);
                const double cur_lon = std::lerp(w1.position.longitude_deg, w2.position.longitude_deg, alpha);
                const float cur_alt = std::lerp(w1.position.altitude_msl_m, w2.position.altitude_msl_m, alpha);

                const float terrain_alt = dem.sample_altitude(cur_lat, cur_lon);
                const float clearance = cur_alt - terrain_alt;

                report.min_terrain_clearance_m = std::min(report.min_terrain_clearance_m, clearance);

                if (clearance < min_clearance_m) {
                    return std::unexpected(FeasibilityError::TerrainCollision);
                }
            }

            // 4. Розрахунок потужності
            const float p_aero = drone.hover_power_watts * (1.0f + 0.05f * std::pow(v_air / 10.0f, 3.0f));
            const float p_climb = (delta_h > 0.0f) ? (drone.mass_kg * 9.81f * climb_rate / 0.65f) : 0.0f;
            const float p_leg = p_aero + p_climb + drone.avionics_power_watts;

            total_energy_joules += p_leg * leg_time;

            if (w2.loiter_time_s > 0.0f) {
                report.total_time_s += w2.loiter_time_s;
                total_energy_joules += (drone.hover_power_watts + drone.avionics_power_watts) * w2.loiter_time_s;
            }
        }

        report.total_energy_wh = total_energy_joules / 3600.0f;

        if (report.total_time_s > max_time_s) {
            return std::unexpected(FeasibilityError::TimeWindowExceeded);
        }

        const float usable_battery_wh = drone.battery_capacity_wh * (1.0f - drone.reserve_margin);
        if (report.total_energy_wh > usable_battery_wh) {
            return std::unexpected(FeasibilityError::InsufficientEnergy);
        }

        report.remaining_battery_pct = (1.0f - (report.total_energy_wh / drone.battery_capacity_wh)) * 100.0f;

        return report;
    }

private:
    struct DistanceBearing {
        float distance_m;
        float bearing_deg;
    };

    static DistanceBearing calc_distance_bearing(const GeoCoordinate& p1, const GeoCoordinate& p2) noexcept {
        const auto d_lat = static_cast<float>((p2.latitude_deg - p1.latitude_deg) * MetersPerDegree);
        const auto lat_rad = static_cast<float>(p1.latitude_deg * (std::numbers::pi_v<double> / 180.0));
        const auto d_lon = static_cast<float>((p2.longitude_deg - p1.longitude_deg) * MetersPerDegree * std::cos(lat_rad));

        const float dist = std::hypot(d_lat, d_lon);
        float bearing = std::atan2(d_lon, d_lat) * (180.0f / std::numbers::pi_v<float>);
        if (bearing < 0.0f) bearing += 360.0f;

        return {dist, bearing};
    }
};
