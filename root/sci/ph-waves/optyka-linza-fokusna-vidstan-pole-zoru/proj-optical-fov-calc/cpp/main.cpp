#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>
#include <format>
#include <optional>

namespace optical {

enum class ErrorCode {
    InvalidParameter,
    ZeroDivision,
    DistanceTooShort
};

struct SensorSpec {
    double width_mm{0.0};
    double height_mm{0.0};
    double pixel_pitch_um{0.0};
    int res_x{0};
    int res_y{0};

    [[nodiscard]] constexpr double diagonal_mm() const noexcept {
        return std::hypot(width_mm, height_mm);
    }

    [[nodiscard]] constexpr double aspect_ratio() const noexcept {
        return height_mm > 0.0 ? width_mm / height_mm : 0.0;
    }
};

struct FovResult {
    double hfov_deg{0.0};
    double vfov_deg{0.0};
    double dfov_deg{0.0};
    double ifov_mrad{0.0};
    double crop_factor{0.0};
    double image_distance_mm{0.0};
};

struct LensSelectionResult {
    double required_focal_length_mm{0.0};
    double magnification{0.0};
    double sensor_distance_mm{0.0};
    bool is_macro_regime{false};
};

struct PyrometerResult {
    double spot_diameter_mm{0.0};
    double ds_ratio{0.0};
    double cone_angle_deg{0.0};
};

class OpticsCalculator {
public:
    static constexpr double FULL_FRAME_DIAG_MM = 43.266615; // sqrt(36^2 + 24^2)

    [[nodiscard]] static constexpr double rad_to_deg(double rad) noexcept {
        return rad * (180.0 / std::numbers::pi);
    }

    [[nodiscard]] static constexpr double deg_to_rad(double deg) noexcept {
        return deg * (std::numbers::pi / 180.0);
    }

    [[nodiscard]] static std::expected<FovResult, ErrorCode> calculate_fov(
        const SensorSpec& sensor,
        double focal_length_mm,
        double working_distance_mm = 0.0) noexcept 
    {
        if (focal_length_mm <= 0.0 || sensor.width_mm <= 0.0 || sensor.height_mm <= 0.0) {
            return std::unexpected(ErrorCode::InvalidParameter);
        }

        double diag = sensor.diagonal_mm();
        double d_i = focal_length_mm;

        if (working_distance_mm > 0.0) {
            if (working_distance_mm <= focal_length_mm) {
                return std::unexpected(ErrorCode::DistanceTooShort);
            }
            d_i = (focal_length_mm * working_distance_mm) / (working_distance_mm - focal_length_mm);
        }

        FovResult res{};
        res.image_distance_mm = d_i;
        res.crop_factor = FULL_FRAME_DIAG_MM / diag;
        res.hfov_deg = rad_to_deg(2.0 * std::atan(sensor.width_mm / (2.0 * d_i)));
        res.vfov_deg = rad_to_deg(2.0 * std::atan(sensor.height_mm / (2.0 * d_i)));
        res.dfov_deg = rad_to_deg(2.0 * std::atan(diag / (2.0 * d_i)));

        double pitch_um = sensor.pixel_pitch_um;
        if (pitch_um <= 0.0 && sensor.res_x > 0) {
            pitch_um = (sensor.width_mm / static_cast<double>(sensor.res_x)) * 1000.0;
        }

        if (pitch_um > 0.0) {
            res.ifov_mrad = (pitch_um / 1000.0) / focal_length_mm * 1000.0;
        }

        return res;
    }

    [[nodiscard]] static std::expected<LensSelectionResult, ErrorCode> select_focal_length(
        double field_width_mm,
        double working_distance_mm,
        double sensor_width_mm) noexcept
    {
        if (field_width_mm <= 0.0 || working_distance_mm <= 0.0 || sensor_width_mm <= 0.0) {
            return std::unexpected(ErrorCode::InvalidParameter);
        }

        double m = sensor_width_mm / field_width_mm;
        LensSelectionResult res{};
        res.magnification = m;
        res.is_macro_regime = (m >= 0.1);
        res.required_focal_length_mm = (working_distance_mm * m) / (1.0 + m);
        res.sensor_distance_mm = res.required_focal_length_mm * (1.0 + m);

        return res;
    }

    [[nodiscard]] static std::expected<PyrometerResult, ErrorCode> calculate_pyrometer_spot(
        double ds_ratio,
        double aperture_diam_mm,
        double distance_mm) noexcept
    {
        if (ds_ratio <= 0.0 || distance_mm < 0.0 || aperture_diam_mm < 0.0) {
            return std::unexpected(ErrorCode::InvalidParameter);
        }

        PyrometerResult res{};
        res.ds_ratio = ds_ratio;
        res.spot_diameter_mm = aperture_diam_mm + (distance_mm / ds_ratio);
        res.cone_angle_deg = rad_to_deg(2.0 * std::atan(1.0 / (2.0 * ds_ratio)));

        return res;
    }
};

} // namespace optical
