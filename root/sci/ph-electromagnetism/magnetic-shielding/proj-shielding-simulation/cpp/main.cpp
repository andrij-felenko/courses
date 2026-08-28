#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>
#include <string_view>

namespace physics {

struct ShieldLayer {
    double r_in{};        // Внутрішній радіус, м
    double r_out{};       // Зовнішній радіус, м
    double mu_max{};      // Максимальна відносна проникність
    double b_sat{};       // Індукція насичення, Тл
    double n_power{3.0};  // Показник нелінійності
};

struct ShieldSimulationResult {
    double internal_field_tesla{};
    double shielding_factor{};
    double shielding_db{};
    bool is_any_layer_saturated{false};
};

class MagneticShieldSimulator {
public:
    explicit MagneticShieldSimulator(std::vector<ShieldLayer> layers)
        : m_layers(std::move(layers)) {}

    [[nodiscard]] ShieldSimulationResult simulate(double external_b_tesla) const {
        ShieldSimulationResult result;
        double current_b = external_b_tesla;
        double total_s = 1.0;

        for (std::size_t i = m_layers.size(); i > 0; --i) {
            const std::size_t idx = i - 1;
            const auto& layer = m_layers[idx];

            // Концентрація магнітного потоку у стінці оболонки
            const double flux_concentration = layer.r_out / (layer.r_out - layer.r_in);
            const double b_in_wall = current_b * flux_concentration;

            if (b_in_wall >= layer.b_sat * 0.9) {
                result.is_any_layer_saturated = true;
            }

            const double mu_r = calculate_effective_mu(b_in_wall, layer);
            const double radius_ratio_sq = std::pow(layer.r_in / layer.r_out, 2);
            const double s_i = 1.0 + 0.25 * (std::pow(mu_r - 1.0, 2) / mu_r) * (1.0 - radius_ratio_sq);

            if (idx < m_layers.size() - 1) {
                const double gap_factor = 1.0 - std::pow(layer.r_out / m_layers[idx + 1].r_in, 2);
                total_s *= s_i * gap_factor;
            } else {
                total_s *= s_i;
            }

            current_b /= s_i;
        }

        result.internal_field_tesla = external_b_tesla / total_s;
        result.shielding_factor = total_s;
        result.shielding_db = 20.0 * std::log10(total_s);
        return result;
    }

private:
    std::vector<ShieldLayer> m_layers;

    [[nodiscard]] static double calculate_effective_mu(double b_field, const ShieldLayer& layer) noexcept {
        if (b_field <= 0.0) return layer.mu_max;
        const double ratio = b_field / layer.b_sat;
        if (ratio >= 1.0) return 1.05;

        const double non_linear_factor = std::max(0.0, 1.0 - std::pow(ratio, layer.n_power));
        return std::max(1.0, 1.0 + (layer.mu_max - 1.0) * non_linear_factor);
    }
};

} // namespace physics

int main() {
    using namespace physics;

    const std::vector<ShieldLayer> layers = {
        {.r_in = 0.050, .r_out = 0.051, .mu_max = 150000.0, .b_sat = 0.75, .n_power = 3.0}, // Мю-метал
        {.r_in = 0.080, .r_out = 0.082, .mu_max = 10000.0,  .b_sat = 2.00, .n_power = 2.0}  // Кремниста сталь
    };

    const MagneticShieldSimulator simulator(layers);
    const std::vector<double> test_fields = {50e-6, 1e-3, 10e-3};

    std::cout << "=== Чисельне моделювання магнітного екрана (C++) ===\n";
    std::cout << std::scientific << std::setprecision(2);

    for (const double b_ext : test_fields) {
        const auto res = simulator.simulate(b_ext);
        std::cout << "B_ext = " << b_ext << " T | B_int = " << res.internal_field_tesla
                  << " T | S = " << res.shielding_factor
                  << " (" << std::fixed << std::setprecision(1) << res.shielding_db << " dB)"
                  << " | Насичення: " << (res.is_any_layer_saturated ? "ТАК" : "НІ") << "\n";
    }

    return 0;
}
