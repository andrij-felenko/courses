#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>
#include <span>
#include <algorithm>
#include <chrono>

namespace tracker {

struct GeoCoord {
    double lat{0.0}; // Градуси (-90.0 .. +90.0)
    double lon{0.0}; // Градуси (-180.0 .. +180.0)
    double alt{0.0}; // Метри AMSL
};

struct TargetAngles {
    double azimuth_deg{0.0};   // 0.0 .. 360.0
    double elevation_deg{0.0}; // 0.0 .. 90.0
    double slant_range_m{0.0}; // Пряма лінійна дальність
};

struct ServoPwm {
    uint16_t pan_us{1500};
    uint16_t tilt_us{1000};
};

enum class TrackerError {
    HomeNotSet,
    InvalidCoordinates,
    Timeout
};

class AntennaTracker {
public:
    constexpr static double EarthRadiusM = 6371000.0;

    explicit AntennaTracker(double max_slew_rate_deg_s = 45.0, double deadband_deg = 1.5)
        : max_slew_rate_{max_slew_rate_deg_s}, deadband_{deadband_deg} {}

    void set_home(const GeoCoord& home) noexcept {
        home_pos_ = home;
        has_home_ = true;
    }

    [[nodiscard]] std::expected<TargetAngles, TrackerError>
    calculate_target(const GeoCoord& uav) const noexcept {
        if (!has_home_) {
            return std::unexpected(TrackerError::HomeNotSet);
        }

        constexpr double deg2rad = std::numbers::pi / 180.0;
        constexpr double rad2deg = 180.0 / std::numbers::pi;

        const double phi1 = home_pos_.lat * deg2rad;
        const double phi2 = uav.lat * deg2rad;
        const double d_phi = (uav.lat - home_pos_.lat) * deg2rad;
        const double d_lambda = (uav.lon - home_pos_.lon) * deg2rad;

        // Ортодромічна дистанція на поверхні еліпсоїда (сферичне наближення)
        const double a = std::sin(d_phi / 2.0) * std::sin(d_phi / 2.0) +
                         std::cos(phi1) * std::cos(phi2) *
                         std::sin(d_lambda / 2.0) * std::sin(d_lambda / 2.0);
        const double c = 2.0 * std::atan2(std::sqrt(a), std::sqrt(1.0 - a));
        const double ground_distance = EarthRadiusM * c;

        // Істинний азимут (Great Circle Initial Bearing)
        const double y = std::sin(d_lambda) * std::cos(phi2);
        const double x = std::cos(phi1) * std::sin(phi2) -
                         std::sin(phi1) * std::cos(phi2) * std::cos(d_lambda);
        double azimuth = std::atan2(y, x) * rad2deg;
        if (azimuth < 0.0) {
            azimuth += 360.0;
        }

        // Корекція кривини Землі для кута елевації
        const double curvature_drop = (ground_distance * ground_distance) / (2.0 * EarthRadiusM);
        const double delta_alt = (uav.alt - home_pos_.alt) - curvature_drop;

        double elevation = std::atan2(delta_alt, ground_distance) * rad2deg;
        elevation = std::clamp(elevation, 0.0, 90.0);

        const double slant_range = std::hypot(ground_distance, delta_alt);

        return TargetAngles{azimuth, elevation, slant_range};
    }

    [[nodiscard]] ServoPwm update(const GeoCoord& uav, double dt_sec) noexcept {
        auto target = calculate_target(uav);
        if (!target) {
            return ServoPwm{1500, 1000};
        }

        // Азимутальна фільтрація найкоротшого шляху
        double d_az = target->azimuth_deg - current_azimuth_;
        while (d_az > 180.0) d_az -= 360.0;
        while (d_az < -180.0) d_az += 360.0;

        if (std::abs(d_az) > deadband_) {
            const double max_step = max_slew_rate_ * dt_sec;
            d_az = std::clamp(d_az, -max_step, max_step);
            current_azimuth_ += d_az;
            if (current_azimuth_ >= 360.0) current_azimuth_ -= 360.0;
            if (current_azimuth_ < 0.0) current_azimuth_ += 360.0;
        }

        // Елеваційна фільтрація
        double d_el = target->elevation_deg - current_elevation_;
        if (std::abs(d_el) > deadband_) {
            const double max_step = max_slew_rate_ * dt_sec;
            d_el = std::clamp(d_el, -max_step, max_step);
            current_elevation_ += d_el;
        }

        // Перетворення в ШІМ мікросекунди
        auto pan_us = static_cast<uint16_t>(1000.0 + (current_azimuth_ / 360.0) * 1000.0);
        auto tilt_us = static_cast<uint16_t>(1000.0 + (current_elevation_ / 90.0) * 1000.0);

        return ServoPwm{pan_us, tilt_us};
    }

private:
    GeoCoord home_pos_{};
    bool has_home_{false};
    double current_azimuth_{0.0};
    double current_elevation_{0.0};
    double max_slew_rate_{45.0};
    double deadband_{1.5};
};

} // namespace tracker
