#include <iostream>
#include <iomanip>
#include <cmath>
#include <expected>

namespace thermal {

inline constexpr double kStefanBoltzmann = 5.670374e-8;

enum class ErrorCode { InvalidDimensions, NonConvergence };

struct Enclosure {
    double length_m{0.120};
    double width_m{0.080};
    double height_m{0.050};
    double wall_thick_m{0.003};
    double wall_conductivity_k{160.0}; // Алюміній = 160, ABS = 0.20
    double emissivity{0.88};           // Анодований метал = 0.88, чистий = 0.08
    double ambient_temp_c{35.0};

    [[nodiscard]] constexpr double total_area() const noexcept {
        return 2.0 * (length_m * width_m + (length_m + width_m) * height_m);
    }
};

struct Component {
    double power_watts{4.5};
    double r_th_jc{3.5};
    double r_th_bridge{1.5}; // Gap Pad на корпус
    double max_allowed_tj_c{105.0};
};

struct ThermalProfile {
    double outer_wall_c{0.0};
    double inner_wall_c{0.0};
    double case_temp_c{0.0};
    double junction_temp_c{0.0};
    double r_th_external{0.0};
    bool   is_within_limits{false};
};

class ThermalModel {
public:
    [[nodiscard]] static std::expected<ThermalProfile, ErrorCode>
    evaluate(const Enclosure& enc, const Component& comp) noexcept {
        if (enc.length_m <= 0.0 || enc.width_m <= 0.0 || enc.height_m <= 0.0) {
            return std::unexpected(ErrorCode::InvalidDimensions);
        }

        const double a_tot = enc.total_area();
        const double r_wall = enc.wall_thick_m / (enc.wall_conductivity_k * a_tot);
        const double t_amb_k = enc.ambient_temp_c + 273.15;
        double t_wall_out = enc.ambient_temp_c + 10.0;
        double final_r_ext = 0.0;

        for (int i = 0; i < 50; ++i) {
            double dt = std::abs(t_wall_out - enc.ambient_temp_c);
            if (dt < 0.1) dt = 0.1;

            double h_c = 1.42 * std::pow(dt / enc.height_m, 0.25);
            if (h_c < 2.5) h_c = 2.5;

            double t_mean_k = 0.5 * ((t_wall_out + 273.15) + t_amb_k);
            double h_r = 4.0 * enc.emissivity * kStefanBoltzmann * std::pow(t_mean_k, 3.0);

            final_r_ext = 1.0 / ((h_c + h_r) * a_tot);
            double next_t = enc.ambient_temp_c + comp.power_watts * final_r_ext;

            if (std::abs(next_t - t_wall_out) < 0.005) {
                t_wall_out = next_t;
                break;
            }
            t_wall_out = 0.6 * t_wall_out + 0.4 * next_t;
        }

        ThermalProfile res{};
        res.outer_wall_c    = t_wall_out;
        res.inner_wall_c    = t_wall_out + comp.power_watts * r_wall;
        res.case_temp_c     = res.inner_wall_c + comp.power_watts * comp.r_th_bridge;
        res.junction_temp_c = res.case_temp_c + comp.power_watts * comp.r_th_jc;
        res.r_th_external   = final_r_ext;
        res.is_within_limits = (res.junction_temp_c < comp.max_allowed_tj_c);

        return res;
    }
};

} // namespace thermal
