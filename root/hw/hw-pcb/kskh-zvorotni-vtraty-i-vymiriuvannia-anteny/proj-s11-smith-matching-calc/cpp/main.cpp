#include <iostream>
#include <iomanip>
#include <complex>
#include <vector>
#include <string>
#include <string_view>
#include <numbers>
#include <cmath>
#include <optional>
#include <span>
#include <algorithm>
#include <format>

namespace rf {

using Complex = std::complex<double>;
constexpr double PI = std::numbers::pi;

// Модель паразитарних параметрів компонентів SMD 0402
struct Parasitics {
    double c_esl_nh{0.35};    // ESL керамічного конденсатора, нГн
    double c_esr_ohm{0.08};   // ESR конденсатора, Ом
    double l_q0{45.0};        // Власна добротність котушки на f0
    double l_cp_pf{0.04};     // Паразитна міжелектродна ємність котушки, пФ
    double pad_cap_pf{0.05};  // Паразитна ємність монтажного майданчика PCB, пФ
};

enum class ComponentType { Inductor, Capacitor };

struct ComponentSpec {
    ComponentType type;
    bool is_series;
    double value_si; // Генрі або Фаради

    [[nodiscard]] double in_units() const noexcept {
        return (type == ComponentType::Inductor) ? value_si * 1e9 : value_si * 1e12;
    }

    [[nodiscard]] std::string_view unit_str() const noexcept {
        return (type == ComponentType::Inductor) ? "нГн" : "пФ";
    }
};

struct MatchingNetwork {
    std::string name;
    double q_loaded{0.0};
    std::vector<ComponentSpec> components;
};

struct RfPoint {
    double freq_hz{0.0};
    Complex s11{0.0, 0.0};
    Complex z_in{0.0, 0.0};
    double vswr{1.0};
    double return_loss_db{0.0};
    double insertion_loss_db{0.0};
};

class RfCalculator {
public:
    static constexpr std::array<double, 24> E24 = {
        1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
        3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
    };

    static double snap_e24(double value) noexcept {
        if (value <= 0.0) return 0.0;
        const double dec = std::pow(10.0, std::floor(std::log10(value)));
        const double norm = value / dec;
        auto it = std::min_element(E24.begin(), E24.end(), [norm](double a, double b) {
            return std::abs(norm - a) < std::abs(norm - b);
        });
        return (*it) * dec;
    }

    static Complex s11_to_z(Complex s11, double z0 = 50.0) noexcept {
        const Complex num = 1.0 + s11;
        const Complex den = 1.0 - s11;
        return (num / den) * z0;
    }

    static Complex z_to_s11(Complex z, double z0 = 50.0) noexcept {
        return (z - z0) / (z + z0);
    }

    static std::vector<MatchingNetwork> synthesize_l_match(Complex z_load, double f0, double z0 = 50.0) {
        std::vector<MatchingNetwork> res;
        const double r_a = z_load.real();
        const double x_a = z_load.imag();
        const double omega = 2.0 * PI * f0;

        if (r_a <= 1e-4 || f0 <= 0.0) return res;

        if (r_a < z0) {
            const double q = std::sqrt((z0 / r_a) - 1.0);
            const double x_s = (q * r_a) - x_a;
            const double b_p = q / z0;

            if (x_s > 0.0 && b_p > 0.0) {
                res.push_back({
                    .name = "L-Match Low-Pass (R_A < Z₀)",
                    .q_loaded = q,
                    .components = {
                        {ComponentType::Inductor, true, x_s / omega},
                        {ComponentType::Capacitor, false, b_p / omega}
                    }
                });
            }
        } else {
            const double q = std::sqrt((r_a / z0) - 1.0);
            const double b_p = q / r_a;
            const double x_s = (q * z0) - x_a;

            if (b_p > 0.0 && x_s > 0.0) {
                res.push_back({
                    .name = "L-Match Low-Pass (R_A > Z₀)",
                    .q_loaded = q,
                    .components = {
                        {ComponentType::Capacitor, false, b_p / omega},
                        {ComponentType::Inductor, true, x_s / omega}
                    }
                });
            }
        }
        return res;
    }

    static std::optional<MatchingNetwork> synthesize_pi_match(
        Complex z_load, 
        double f0, 
        double q_target = 3.0, 
        double z0 = 50.0) 
    {
        const double r_a = z_load.real();
        const double x_a = z_load.imag();
        const double omega = 2.0 * PI * f0;

        const double r_min = std::min(r_a, z0);
        const double r_v = r_min / (1.0 + q_target * q_target);

        if (r_v >= z0 || r_v >= r_a) return std::nullopt;

        const double q1 = std::sqrt((z0 / r_v) - 1.0);
        const double q2 = std::sqrt((r_a / r_v) - 1.0);

        const double b_p1 = q1 / z0;
        const double b_p2 = q2 / r_a;
        const double x_s = (q1 * r_v) + (q2 * r_v) - x_a;

        if (b_p1 <= 0.0 || b_p2 <= 0.0 || x_s <= 0.0) return std::nullopt;

        return MatchingNetwork{
            .name = "Pi-Match Harmonic Filter",
            .q_loaded = q_target,
            .components = {
                {ComponentType::Capacitor, false, b_p1 / omega},
                {ComponentType::Inductor, true, x_s / omega},
                {ComponentType::Capacitor, false, b_p2 / omega}
            }
        };
    }

    static Complex eval_capacitor(double c_val, double freq_hz, const Parasitics& p) noexcept {
        const double omega = 2.0 * PI * freq_hz;
        const double esl = p.c_esl_nh * 1e-9;
        const double x_c = (omega * esl) - (1.0 / (omega * c_val));
        return {p.c_esr_ohm, x_c};
    }

    static Complex eval_inductor(double l_val, double freq_hz, const Parasitics& p) noexcept {
        const double omega = 2.0 * PI * freq_hz;
        const double esr = (omega * l_val) / std::max(p.l_q0, 1.0);
        const Complex z_l{esr, omega * l_val};
        const double cp = p.l_cp_pf * 1e-12;
        if (cp > 1e-15) {
            const Complex z_cp{0.0, -1.0 / (omega * cp)};
            return (z_l * z_cp) / (z_l + z_cp);
        }
        return z_l;
    }

    static std::vector<RfPoint> simulate_sweep(
        const MatchingNetwork& net, 
        Complex z_ant_f0, 
        double f0, 
        double z0 = 50.0, 
        const Parasitics& p = {}) 
    {
        std::vector<RfPoint> out;
        const double f_start = f0 * 0.85;
        const double f_stop = f0 * 1.15;
        constexpr int steps = 11;

        for (int i = 0; i < steps; ++i) {
            const double f = f_start + (static_cast<double>(i) * (f_stop - f_start) / (steps - 1));
            const double x_ant = z_ant_f0.imag() + 2.0 * (f - f0) / f0 * 50.0;
            Complex z_node{z_ant_f0.real(), x_ant};

            if (net.components.size() == 3) {
                // Pi-Match: C2 || ( L + ( C1 || Z_in ) )
                const Complex z_c2 = eval_capacitor(net.components[2].value_si, f, p);
                z_node = (z_node * z_c2) / (z_node + z_c2);
                const Complex z_l = eval_inductor(net.components[1].value_si, f, p);
                z_node += z_l;
                const Complex z_c1 = eval_capacitor(net.components[0].value_si, f, p);
                z_node = (z_node * z_c1) / (z_node + z_c1);
            } else if (net.components.size() == 2) {
                // L-Match
                if (net.components[0].is_series) {
                    const Complex z_s = (net.components[0].type == ComponentType::Inductor)
                        ? eval_inductor(net.components[0].value_si, f, p)
                        : eval_capacitor(net.components[0].value_si, f, p);
                    z_node += z_s;
                    const Complex z_p = (net.components[1].type == ComponentType::Capacitor)
                        ? eval_capacitor(net.components[1].value_si, f, p)
                        : eval_inductor(net.components[1].value_si, f, p);
                    z_node = (z_node * z_p) / (z_node + z_p);
                } else {
                    const Complex z_p = (net.components[0].type == ComponentType::Capacitor)
                        ? eval_capacitor(net.components[0].value_si, f, p)
                        : eval_inductor(net.components[0].value_si, f, p);
                    z_node = (z_node * z_p) / (z_node + z_p);
                    const Complex z_s = (net.components[1].type == ComponentType::Inductor)
                        ? eval_inductor(net.components[1].value_si, f, p)
                        : eval_capacitor(net.components[1].value_si, f, p);
                    z_node += z_s;
                }
            }

            const Complex s11 = z_to_s11(z_node, z0);
            const double mag = std::abs(s11);
            const double vswr = (mag >= 0.999) ? 99.9 : (1.0 + mag) / (1.0 - mag);
            const double rl = (mag < 1e-6) ? 80.0 : -20.0 * std::log10(mag);
            const double p_trans = std::max(1.0 - mag * mag, 1e-6);
            const double il = -10.0 * std::log10(p_trans);

            out.push_back({
                .freq_hz = f,
                .s11 = s11,
                .z_in = z_node,
                .vswr = vswr,
                .return_loss_db = rl,
                .insertion_loss_db = il
            });
        }
        return out;
    }
};

} // namespace rf

int main(int argc, char** argv) {
    std::cout << "===================================================================\n";
    std::cout << " RF IMPEDANCE MATCHING & S11 SYNTHESIS CALCULATOR (C++20)\n";
    std::cout << "===================================================================\n";

    double f0 = 2440.0 * 1e6;
    constexpr double z0 = 50.0;
    rf::Complex z_ant{18.0, -42.0};

    if (argc >= 4) {
        f0 = std::stod(argv[1]) * 1e6;
        z_ant = {std::stod(argv[2]), std::stod(argv[3])};
    }

    std::cout << std::format("Частота f₀:        {:.2f} МГц\n", f0 * 1e-6);
    std::cout << std::format("Опорний Z₀:        {:.1f} Ом\n", z0);
    std::cout << std::format("Імпеданс антени:   {:.2f} {} j{:.2f} Ом\n\n",
                             z_ant.real(), z_ant.imag() >= 0 ? '+' : '-', std::abs(z_ant.imag()));

    const rf::Complex s11_init = rf::RfCalculator::z_to_s11(z_ant, z0);
    const double mag_init = std::abs(s11_init);
    const double vswr_init = (1.0 + mag_init) / (1.0 - mag_init);
    const double rl_init = -20.0 * std::log10(mag_init);

    std::cout << std::format("Характеристики антени до узгодження:\n");
    std::cout << std::format("  |S₁₁|:           {:.4f} ({:.2f} дБ)\n", mag_init, -rl_init);
    std::cout << std::format("  КСХ (VSWR):      {:.2f}\n", vswr_init);
    std::cout << std::format("  Потужність в ан.: {:.1f} %\n\n", (1.0 - mag_init * mag_init) * 100.0);

    const auto l_networks = rf::RfCalculator::synthesize_l_match(z_ant, f0, z0);
    std::cout << "=== СИНТЕЗ ДВОЕЛЕМЕНТНИХ L-КОНТУРІВ ===\n";
    for (size_t i = 0; i < l_networks.size(); ++i) {
        std::cout << std::format("[{}] {} (Q_L = {:.2f}):\n", i + 1, l_networks[i].name, l_networks[i].q_loaded);
        for (const auto& comp : l_networks[i].components) {
            const double val_units = comp.in_units();
            const double e24_val = rf::RfCalculator::snap_e24(val_units);
            std::cout << std::format("    {} {}: {:.2f} {} (E24: {:.2f} {})\n",
                                     comp.is_series ? "Послідовний" : "Шунтовий",
                                     comp.type == rf::ComponentType::Inductor ? 'L' : 'C',
                                     val_units, comp.unit_str(), e24_val, comp.unit_str());
        }
    }

    const auto pi_net = rf::RfCalculator::synthesize_pi_match(z_ant, f0, 3.0, z0);
    if (pi_net) {
        std::cout << std::format("\n=== СИНТЕЗ ТРЬОХЕЛЕМЕНТНОГО П-КОНТУРУ (Q_L = {:.1f}) ===\n", pi_net->q_loaded);
        for (const auto& comp : pi_net->components) {
            const double val_units = comp.in_units();
            const double e24_val = rf::RfCalculator::snap_e24(val_units);
            std::cout << std::format("    {} {}: {:.2f} {} (E24: {:.2f} {})\n",
                                     comp.is_series ? "Послідовний" : "Шунтовий",
                                     comp.type == rf::ComponentType::Inductor ? 'L' : 'C',
                                     val_units, comp.unit_str(), e24_val, comp.unit_str());
        }
    }

    if (!l_networks.empty()) {
        std::cout << "\n=== РЕЗУЛЬТАТИ ЧАСТОТНОЇ РОЗГОРТКИ ДЛЯ L-MATCH (C++20) ===\n";
        std::cout << "Частота [МГц] | S₁₁ [дБ] |  КСХ   | Втрати [дБ] | Вхідний Z_in [Ом]\n";
        std::cout << "--------------+----------+--------+-------------+------------------\n";
        const auto sweep = rf::RfCalculator::simulate_sweep(l_networks[0], z_ant, f0, z0);
        for (const auto& pt : sweep) {
            std::cout << std::format("  {:7.1f}     |  {:6.2f}  |  {:5.2f} |    {:5.2f}    | {:5.1f} + j{:5.1f}\n",
                                     pt.freq_hz * 1e-6, -pt.return_loss_db, pt.vswr, pt.insertion_loss_db,
                                     pt.z_in.real(), pt.z_in.imag());
        }
    }

    return 0;
}
