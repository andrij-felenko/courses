#include <iostream>
#include <iomanip>
#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>
#include <vector>

namespace rf {

inline constexpr double SpeedOfLightMmNs = 299.792458;
inline constexpr double Eta0 = 376.7303135;

enum class CalculationError {
    InvalidSubstrateParameters,
    TargetImpedanceOutOfRange,
    ConvergenceFailed
};

struct Substrate {
    double relative_permittivity{3.66};
    double height_mm{0.508};
    double copper_thickness_mm{0.035};
    double loss_tangent{0.0037};

    [[nodiscard]] constexpr bool is_valid() const noexcept {
        return relative_permittivity >= 1.0 && height_mm > 0.0 && copper_thickness_mm >= 0.0;
    }
};

struct MicrostripSynthesis {
    double width_mm{0.0};
    double normalized_width{0.0};
    double characteristic_impedance{0.0};
    double static_effective_permittivity{0.0};
    double dispersed_effective_permittivity{0.0};
    double guided_wavelength_mm{0.0};
    double phase_velocity_mm_ns{0.0};
    double velocity_factor{0.0};
    double end_extension_delta_l_mm{0.0};
    double physical_quarter_wave_mm{0.0};
};

struct StubSynthesisResult {
    double distance_to_load_mm{0.0};
    double stub_physical_length_mm{0.0};
    double stub_width_mm{0.0};
    double stub_impedance_ohms{0.0};
};

struct FrequencyPoint {
    double frequency_ghz{0.0};
    double dispersed_permittivity{0.0};
    double reflection_magnitude{0.0};
    double return_loss_db{0.0};
    double vswr{0.0};
};

class MicrostripEngine {
public:
    [[nodiscard]] static constexpr double static_permittivity(double u, double er) noexcept {
        const double a_u = 1.0 + (1.0 / 49.0) * std::log((std::pow(u, 4) + std::pow(u / 52.0, 2)) / (std::pow(u, 4) + 0.432))
                           + (1.0 / 18.7) * std::log(1.0 + std::pow(u / 18.1, 3));
        const double b_er = 0.564 * std::pow((er - 0.9) / (er + 3.0), 0.05);
        const double factor = std::pow(1.0 + 10.0 / u, -a_u * b_er);
        return ((er + 1.0) / 2.0) + ((er - 1.0) / 2.0) * factor;
    }

    [[nodiscard]] static double impedance_from_u(double u, double er) noexcept {
        const double eps_eff = static_permittivity(u, er);
        if (u <= 1.0) {
            const double f_u = 6.0 + (2.0 * std::numbers::pi - 6.0) * std::exp(-std::pow(30.666 / u, 0.752));
            return (Eta0 / (2.0 * std::numbers::pi * std::sqrt(eps_eff)))
                   * std::log(f_u / u + std::sqrt(1.0 + std::pow(2.0 / u, 2)));
        }
        return (Eta0 / std::sqrt(eps_eff)) * (1.0 / (u + 1.393 + 0.667 * std::log(u + 1.444)));
    }

    [[nodiscard]] static double kirschning_jansen_dispersion(double u, double er, double h_mm,
                                                             double f_ghz, double eps_eff_0) noexcept {
        const double fn = f_ghz * (h_mm * 0.1);
        const double p1 = 0.27488 + (0.6315 + 0.525 / std::pow(1.0 + 0.0157 * fn, 20.0)) * u
                          - 0.065683 * std::exp(-8.7513 * u);
        const double p2 = 0.33622 * (1.0 - std::exp(-0.03442 * er));
        const double p3 = 0.0363 * std::exp(-4.6 * u) * (1.0 - std::exp(-std::pow(fn / 3.87, 4.97)));
        const double p4 = 1.0 + 2.751 * (1.0 - std::exp(-std::pow(er / 15.916, 8.0)));
        const double p_f = p1 * p2 * std::pow((0.1844 + p3 * p4) * 10.0 * fn, 1.5763);

        return er - ((er - eps_eff_0) / (1.0 + p_f));
    }

    [[nodiscard]] static double end_effect_extension(double u, double eps_eff, double h_mm) noexcept {
        const double factor = 0.412 * ((eps_eff + 0.3) / (eps_eff - 0.258)) * ((u + 0.264) / (u + 0.8));
        return factor * h_mm;
    }

    [[nodiscard]] static std::expected<MicrostripSynthesis, CalculationError>
    synthesize(const Substrate& sub, double target_z0_ohms, double freq_ghz) noexcept {
        if (!sub.is_valid()) {
            return std::unexpected(CalculationError::InvalidSubstrateParameters);
        }
        if (target_z0_ohms <= 5.0 || target_z0_ohms >= 200.0) {
            return std::unexpected(CalculationError::TargetImpedanceOutOfRange);
        }

        double u_min = 0.001;
        double u_max = 100.0;
        double u_found = 0.0;
        bool converged = false;

        for (int iter = 0; iter < 100; ++iter) {
            const double u_mid = 0.5 * (u_min + u_max);
            const double z_calc = impedance_from_u(u_mid, sub.relative_permittivity);
            if (std::abs(z_calc - target_z0_ohms) < 1e-6) {
                u_found = u_mid;
                converged = true;
                break;
            }
            if (z_calc > target_z0_ohms) {
                u_min = u_mid;
            } else {
                u_max = u_mid;
            }
        }

        if (!converged) {
            u_found = 0.5 * (u_min + u_max);
        }

        MicrostripSynthesis out{};
        out.normalized_width = u_found;
        out.width_mm = u_found * sub.height_mm;
        out.characteristic_impedance = impedance_from_u(u_found, sub.relative_permittivity);
        out.static_effective_permittivity = static_permittivity(u_found, sub.relative_permittivity);
        out.dispersed_effective_permittivity = kirschning_jansen_dispersion(
            u_found, sub.relative_permittivity, sub.height_mm, freq_ghz, out.static_effective_permittivity
        );

        const double lambda_0 = SpeedOfLightMmNs / freq_ghz;
        out.guided_wavelength_mm = lambda_0 / std::sqrt(out.dispersed_effective_permittivity);
        out.phase_velocity_mm_ns = SpeedOfLightMmNs / std::sqrt(out.dispersed_effective_permittivity);
        out.velocity_factor = out.phase_velocity_mm_ns / SpeedOfLightMmNs;
        out.end_extension_delta_l_mm = end_effect_extension(u_found, out.dispersed_effective_permittivity, sub.height_mm);
        out.physical_quarter_wave_mm = (out.guided_wavelength_mm * 0.25) - out.end_extension_delta_l_mm;

        return out;
    }

    [[nodiscard]] static std::expected<StubSynthesisResult, CalculationError>
    synthesize_stub(const Substrate& sub, double z0_feed, double r_load, double x_load, double freq_ghz) noexcept {
        auto feed_res = synthesize(sub, z0_feed, freq_ghz);
        if (!feed_res) return std::unexpected(feed_res.error());
        const auto& feed = *feed_res;

        const double z_mag2 = r_load * r_load + x_load * x_load;
        const double g_load = (r_load / z_mag2) * z0_feed;
        const double b_load = (-x_load / z_mag2) * z0_feed;

        double t = 0.0;
        if (std::abs(g_load - 1.0) < 1e-5) {
            t = 0.0;
        } else {
            t = (b_load + std::sqrt(g_load * (std::pow(1.0 - g_load, 2) + b_load * b_load))) / (g_load - 1.0);
        }

        double theta_d = std::atan(t);
        if (theta_d < 0.0) theta_d += std::numbers::pi;
        const double dist_mm = (theta_d / (2.0 * std::numbers::pi)) * feed.guided_wavelength_mm;

        const double b_in = (b_load + g_load * g_load * t + b_load * b_load * t - t)
                            / (std::pow(1.0 - b_load * t, 2) + std::pow(g_load * t, 2));
        const double b_stub = -b_in;

        double theta_stub = std::atan(b_stub);
        if (theta_stub < 0.0) theta_stub += std::numbers::pi;
        const double l_stub_ideal = (theta_stub / (2.0 * std::numbers::pi)) * feed.guided_wavelength_mm;
        const double l_stub_phys = l_stub_ideal - feed.end_extension_delta_l_mm;

        return StubSynthesisResult{
            .distance_to_load_mm = dist_mm,
            .stub_physical_length_mm = l_stub_phys,
            .stub_width_mm = feed.width_mm,
            .stub_impedance_ohms = z0_feed
        };
    }

    [[nodiscard]] static std::vector<FrequencyPoint>
    sweep_transformer(const Substrate& sub, double z_feed, double z_load,
                      const MicrostripSynthesis& trans, double f_center_ghz) {
        std::vector<FrequencyPoint> sweep{};
        const double fixed_length_mm = trans.guided_wavelength_mm * 0.25;

        for (double f = f_center_ghz - 2.0; f <= f_center_ghz + 2.001; f += 0.5) {
            const double eps_f = kirschning_jansen_dispersion(
                trans.normalized_width, sub.relative_permittivity, sub.height_mm, f, trans.static_effective_permittivity
            );
            const double beta = (2.0 * std::numbers::pi * f / SpeedOfLightMmNs) * std::sqrt(eps_f);
            const double theta = beta * fixed_length_mm;

            const double cos_th = std::cos(theta);
            const double sin_th = std::sin(theta);

            const double re_num = z_load * cos_th;
            const double im_num = trans.characteristic_impedance * sin_th;
            const double re_den = cos_th;
            const double im_den = (z_load / trans.characteristic_impedance) * sin_th;

            const double den_mag2 = re_den * re_den + im_den * im_den;
            const double z_in_re = (re_num * re_den + im_num * im_den) / den_mag2;
            const double z_in_im = (im_num * re_den - re_num * im_den) / den_mag2;

            const double num_re = z_in_re - z_feed;
            const double num_im = z_in_im;
            const double den_re = z_in_re + z_feed;
            const double den_im = z_in_im;

            const double gamma = std::sqrt((num_re * num_re + num_im * num_im) / (den_re * den_re + den_im * den_im));
            const double rl = (gamma > 1e-5) ? -20.0 * std::log10(gamma) : 60.0;
            const double vswr = (1.0 + gamma) / (1.0 - gamma);

            sweep.push_back(FrequencyPoint{
                .frequency_ghz = f,
                .dispersed_permittivity = eps_f,
                .reflection_magnitude = gamma,
                .return_loss_db = rl,
                .vswr = vswr
            });
        }
        return sweep;
    }
};

} // namespace rf

int main() {
    rf::Substrate rogers4350{
        .relative_permittivity = 3.66,
        .height_mm = 0.508,
        .copper_thickness_mm = 0.035,
        .loss_tangent = 0.0037
    };
    constexpr double FrequencyGhz = 5.80;

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== СИНТЕЗ МІКРОСМУЖКОВИХ ЕЛЕМЕНТІВ (C++20) ===\n";
    std::cout << "Підкладка: Rogers RO4350B, f = " << FrequencyGhz << " ГГц\n\n";

    auto line50_result = rf::MicrostripEngine::synthesize(rogers4350, 50.0, FrequencyGhz);
    if (!line50_result) {
        std::cerr << "Помилка розрахунку 50-омної лінії!\n";
        return 1;
    }
    const auto& l50 = *line50_result;

    std::cout << "1. Магістраль 50 Ом:\n"
              << "   Ширина w: " << l50.width_mm << " мм (w/h = " << l50.normalized_width << ")\n"
              << "   eps_eff(0) = " << l50.static_effective_permittivity
              << " -> eps_eff(" << FrequencyGhz << " ГГц) = " << l50.dispersed_effective_permittivity << "\n"
              << "   lambda_g = " << l50.guided_wavelength_mm << " мм (VF = " << l50.velocity_factor << ")\n"
              << "   Фазова швидкість v_p = " << l50.phase_velocity_mm_ns << " мм/нс\n\n";

    constexpr double TargetLoad = 100.0;
    const double TransformerZ0 = std::sqrt(50.0 * TargetLoad);
    auto trans_result = rf::MicrostripEngine::synthesize(rogers4350, TransformerZ0, FrequencyGhz);
    if (trans_result) {
        const auto& tr = *trans_result;
        std::cout << "2. Трансформатор lambda/4 (" << TransformerZ0 << " Ом):\n"
                  << "   Ширина секції w_T: " << tr.width_mm << " мм\n"
                  << "   Фізична довжина L_T: " << (tr.guided_wavelength_mm * 0.25) << " мм\n\n";

        std::cout << "3. Розімкнений узгоджувальний шлейф 50 Ом:\n"
                  << "   Крайове подовження delta_l: " << l50.end_extension_delta_l_mm << " мм\n"
                  << "   Скоригована довжина L_stub: " << l50.physical_quarter_wave_mm << " мм\n\n";

        auto stub_res = rf::MicrostripEngine::synthesize_stub(rogers4350, 50.0, 25.0, -35.0, FrequencyGhz);
        if (stub_res) {
            const auto& st = *stub_res;
            std::cout << "4. Одношлейфовий узгоджувач для Z_L = 25 - j*35 Ом:\n"
                      << "   Відстань d від навантаження: " << st.distance_to_load_mm << " мм\n"
                      << "   Довжина розімкненого шлейфа: " << st.stub_physical_length_mm << " мм\n\n";
        }

        auto sweep = rf::MicrostripEngine::sweep_transformer(rogers4350, 50.0, TargetLoad, tr, FrequencyGhz);
        std::cout << "--- Частотна характеристика узгодження (C++20) ---\n";
        std::cout << " Частота (ГГц) | eps_eff(f) |  |S11|  | Return Loss (дБ) |  КСХ  \n";
        std::cout << "---------------+------------+--------+------------------+-------\n";
        for (const auto& pt : sweep) {
            std::cout << "    " << std::setw(5) << std::setprecision(2) << pt.frequency_ghz << "      |   "
                      << std::setw(6) << std::setprecision(4) << pt.dispersed_permittivity << "   | "
                      << std::setw(6) << std::setprecision(4) << pt.reflection_magnitude << " |      "
                      << std::setw(6) << std::setprecision(2) << pt.return_loss_db << "      | "
                      << std::setw(5) << std::setprecision(2) << pt.vswr << " \n";
        }
    }

    return 0;
}
