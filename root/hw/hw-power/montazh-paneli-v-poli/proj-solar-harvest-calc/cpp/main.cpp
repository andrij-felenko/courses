#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <numeric>
#include <span>

struct SolarPanel {
    double p_stc_w{100.0};       // Номінальна потужність за STC (Вт)
    double gamma_pmp{-0.38};      // Температурний коефіцієнт Pmax (%/°C)
    double noct_c{45.0};          // Нормальна робоча температура комірки (°C)
    double tilt_deg{60.0};        // Кут нахилу панелі до горизонту (°)
    double azimuth_deg{0.0};      // Азимут (0° = суворо на Південь)
    double soiling_factor{0.05};  // Коефіцієнт втрат від бруду (5%)
};

struct HarvestMetrics {
    std::vector<double> daily_kwh;
    double annual_kwh{0.0};
    double min_day_kwh{0.0};
    double max_day_kwh{0.0};
    int worst_day{1};
};

class SolarSimulator {
public:
    explicit SolarSimulator(double latitude_deg) : latitude_deg_{latitude_deg} {}

    [[nodiscard]] HarvestMetrics simulate(const SolarPanel& panel) const {
        HarvestMetrics result;
        result.daily_kwh.resize(365, 0.0);

        for (int day = 1; day <= 365; ++day) {
            double daily_wh = 0.0;
            const double t_ambient = estimate_ambient_temp(day);

            for (int h = 0; h < 24; ++h) {
                const double hour = h + 0.5;
                daily_wh += instant_power(panel, day, hour, t_ambient);
            }

            const double kwh = daily_wh / 1000.0;
            result.daily_kwh[day - 1] = kwh;
            result.annual_kwh += kwh;
        }

        auto [min_it, max_it] = std::minmax_element(result.daily_kwh.begin(), result.daily_kwh.end());
        result.min_day_kwh = *min_it;
        result.max_day_kwh = *max_it;
        result.worst_day = static_cast<int>(std::distance(result.daily_kwh.begin(), min_it) + 1);

        return result;
    }

private:
    double latitude_deg_{50.45};

    static constexpr double to_rad(double deg) noexcept {
        return deg * (std::numbers::pi / 180.0);
    }

    static double estimate_ambient_temp(int day_of_year) noexcept {
        return 10.0 - 12.0 * std::cos(to_rad(360.0 * (day_of_year - 15) / 365.0));
    }

    [[nodiscard]] double instant_power(const SolarPanel& panel, int day, double hour, double t_amb) const {
        const double lat_rad = to_rad(latitude_deg_);
        const double tilt_rad = to_rad(panel.tilt_deg);
        const double decl_rad = to_rad(23.45 * std::sin(to_rad(360.0 * (284 + day) / 365.0)));
        const double hour_rad = to_rad((hour - 12.0) * 15.0);

        const double sin_elev = std::sin(lat_rad) * std::sin(decl_rad) +
                                std::cos(lat_rad) * std::cos(decl_rad) * std::cos(hour_rad);
        if (sin_elev <= 0.0) return 0.0;

        const double az_rad = to_rad(panel.azimuth_deg);
        const double cos_inc = std::sin(decl_rad) * std::sin(lat_rad) * std::cos(tilt_rad) -
                               std::sin(decl_rad) * std::cos(lat_rad) * std::sin(tilt_rad) * std::cos(az_rad) +
                               std::cos(decl_rad) * std::cos(lat_rad) * std::cos(tilt_rad) * std::cos(hour_rad) +
                               std::cos(decl_rad) * std::sin(lat_rad) * std::sin(tilt_rad) * std::cos(az_rad) * std::cos(hour_rad) +
                               std::cos(decl_rad) * std::sin(tilt_rad) * std::sin(az_rad) * std::sin(hour_rad);
        if (cos_inc <= 0.0) return 0.0;

        const double am = 1.0 / (sin_elev + 0.0001);
        const double g_dir = 1361.0 * std::pow(0.7, std::pow(am, 0.678));
        const double g_dif = 0.12 * g_dir;
        const double g_tilt = g_dir * cos_inc + g_dif * ((1.0 + std::cos(tilt_rad)) / 2.0);

        const double t_cell = t_amb + g_tilt * ((panel.noct_c - 20.0) / 800.0);
        const double temp_derate = std::max(0.2, 1.0 + (panel.gamma_pmp / 100.0) * (t_cell - 25.0));
        const double soil_derate = 1.0 - panel.soiling_factor;

        return panel.p_stc_w * (g_tilt / 1000.0) * temp_derate * soil_derate;
    }
};
