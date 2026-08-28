#include <iostream>
#include <cmath>
#include <array>
#include <numbers>
#include <optional>
#include <iomanip>
#include <algorithm>

namespace gnss::iono {

constexpr double speed_of_light_m_s = 299792458.0;
constexpr double default_l1_freq_hz  = 1575.42e6;

/* Сучасна структура параметрів Клобучара */
struct KlobucharParams {
    std::array<double, 4> alpha{};
    std::array<double, 4> beta{};
};

/* Специфікація спостереження */
struct Observation {
    double latitude_deg{0.0};
    double longitude_deg{0.0};
    double elevation_deg{0.0};
    double azimuth_deg{0.0};
    double gps_time_sec{0.0};
    double frequency_hz{default_l1_freq_hz};
};

class KlobucharCalculator {
public:
    explicit KlobucharCalculator(KlobucharParams params) : params_(params) {}

    [[nodiscard]] double computeDelayMeters(const Observation& obs) const noexcept {
        const double lat_semi  = obs.latitude_deg / 180.0;
        const double lon_semi  = obs.longitude_deg / 180.0;
        const double elev_semi = obs.elevation_deg / 180.0;
        const double azim_rad  = obs.azimuth_deg * (std::numbers::pi / 180.0);

        /* 1. Геометрія пробійної точки */
        const double psi = 0.0137 / (elev_semi + 0.11) - 0.022;

        double lat_i = lat_semi + psi * std::cos(azim_rad);
        lat_i = std::clamp(lat_i, -0.416, 0.416);

        const double lon_i = lon_semi + (psi * std::sin(azim_rad)) / std::cos(lat_i * std::numbers::pi);

        /* 2. Геомагнітна широта IPP */
        const double lat_m = lat_i + 0.064 * std::cos((lon_i - 1.617) * std::numbers::pi);

        /* 3. Сонячний час IPP */
        double t_local = std::fmod(43200.0 * lon_i + obs.gps_time_sec, 86400.0);
        if (t_local < 0.0) t_local += 86400.0;

        /* 4. Похилий фактор */
        const double f_slanted = 1.0 + 16.0 * std::pow(0.53 - elev_semi, 3.0);

        /* 5. Поліноми Амплітуди та Періоду */
        double amp = evaluatePolynomial(params_.alpha, lat_m);
        amp = std::max(0.0, amp);

        double period = evaluatePolynomial(params_.beta, lat_m);
        period = std::max(72000.0, period);

        /* 6. Обчислення часової затримки */
        const double x_phase = 2.0 * std::numbers::pi * (t_local - 50400.0) / period;
        double delay_sec = 0.0;

        if (std::abs(x_phase) < 1.57) {
            const double cos_approx = 1.0 - (x_phase * x_phase) / 2.0 + std::pow(x_phase, 4.0) / 24.0;
            delay_sec = f_slanted * (5.0e-9 + amp * cos_approx);
        } else {
            delay_sec = f_slanted * 5.0e-9;
        }

        /* 7. Масштабування за частотою 1/f² та конверсія у метри */
        const double freq_scale = (default_l1_freq_hz * default_l1_freq_hz) / (obs.frequency_hz * obs.frequency_hz);
        return delay_sec * speed_of_light_m_s * freq_scale;
    }

private:
    static double evaluatePolynomial(const std::array<double, 4>& coeff, double x) noexcept {
        return coeff[0] + coeff[1] * x + coeff[2] * x * x + coeff[3] * x * x * x;
    }

    KlobucharParams params_;
};

} // namespace gnss::iono

int main() {
    using namespace gnss::iono;

    KlobucharParams params{
        .alpha = {0.1490e-07, 0.1490e-07, -0.5960e-07, -0.1192e-06},
        .beta  = {0.9830e+05, 0.8192e+05, -0.1966e+06, -0.4588e+06}
    };

    KlobucharCalculator calc(params);

    Observation obs_l1{
        .latitude_deg  = 50.45,
        .longitude_deg = 30.52,
        .elevation_deg = 35.0,
        .azimuth_deg   = 140.0,
        .gps_time_sec  = 50400.0,
        .frequency_hz  = 1575.42e6
    };

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "[C++] Затримка L1 (50.45N, 30.52E, elev=35 deg): " 
              << calc.computeDelayMeters(obs_l1) << " м\n";

    Observation obs_l2 = obs_l1;
    obs_l2.frequency_hz = 1227.60e6;
    std::cout << "[C++] Затримка L2 (50.45N, 30.52E, elev=35 deg): " 
              << calc.computeDelayMeters(obs_l2) << " м\n";

    return 0;
}
