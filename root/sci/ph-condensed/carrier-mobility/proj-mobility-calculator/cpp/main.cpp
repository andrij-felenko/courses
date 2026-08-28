#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <expected>
#include <string_view>
#include <numbers>

namespace physics::transport {

constexpr double ELEMENTARY_CHARGE = 1.602176634e-19; // Кулони

enum class Material {
    Silicon,
    GalliumArsenide
};

struct CarrierParams {
    double mu_min;   // см²/(В·с)
    double mu_max;   // см²/(В·с)
    double n_ref;    // см⁻³
    double alpha;    // безрозмірний
    double v_sat;    // см/с
    double beta;     // безрозмірний
    double gamma;    // температурний коефіцієнт
};

struct MaterialProfile {
    CarrierParams electron;
    CarrierParams hole;
};

struct TransportMetrics {
    double mu_e_low;     // см²/(В·с)
    double mu_h_low;     // см²/(В·с)
    double v_drift_e;    // см/с
    double v_drift_h;    // см/с
    double mu_e_field;   // см²/(В·с)
    double mu_h_field;   // см²/(В·с)
    double conductivity; // 1/(Ом·см)
    double resistivity;  // Ом·см
};

enum class TransportError {
    InvalidTemperature,
    NegativeDoping,
    NegativeElectricField
};

class MobilitySolver {
public:
    explicit MobilitySolver(Material mat) : material_(mat) {
        if (mat == Material::Silicon) {
            profile_ = MaterialProfile{
                .electron = {.mu_min = 65.0, .mu_max = 1417.0, .n_ref = 9.68e16, .alpha = 0.680, .v_sat = 1.07e7, .beta = 1.11, .gamma = 2.42},
                .hole     = {.mu_min = 47.7, .mu_max = 470.5,  .n_ref = 2.23e17, .alpha = 0.719, .v_sat = 8.37e6, .beta = 1.21, .gamma = 2.20}
            };
        } else {
            profile_ = MaterialProfile{
                .electron = {.mu_min = 500.0, .mu_max = 8500.0, .n_ref = 1.69e17, .alpha = 0.436, .v_sat = 1.20e7, .beta = 2.00, .gamma = 1.50},
                .hole     = {.mu_min = 20.0,  .mu_max = 400.0,  .n_ref = 2.75e17, .alpha = 0.395, .v_sat = 8.00e6, .beta = 1.00, .gamma = 1.50}
            };
        }
    }

    [[nodiscard]] std::expected<TransportMetrics, TransportError> solve(
        double temp_k, double n_donor, double n_acceptor, double electric_field_v_cm) const 
    {
        if (temp_k <= 0.0) return std::unexpected(TransportError::InvalidTemperature);
        if (n_donor < 0.0 || n_acceptor < 0.0) return std::unexpected(TransportError::NegativeDoping);
        if (electric_field_v_cm < 0.0) return std::unexpected(TransportError::NegativeElectricField);

        TransportMetrics res{};
        double n_total = n_donor + n_acceptor;

        res.mu_e_low = calc_low_field_mobility(profile_.electron, temp_k, n_total);
        res.mu_h_low = calc_low_field_mobility(profile_.hole, temp_k, n_total);

        res.v_drift_e = calc_drift_velocity(res.mu_e_low, electric_field_v_cm, profile_.electron.v_sat, profile_.electron.beta);
        res.v_drift_h = calc_drift_velocity(res.mu_h_low, electric_field_v_cm, profile_.hole.v_sat, profile_.hole.beta);

        res.mu_e_field = (electric_field_v_cm > 0.0) ? (res.v_drift_e / electric_field_v_cm) : res.mu_e_low;
        res.mu_h_field = (electric_field_v_cm > 0.0) ? (res.v_drift_h / electric_field_v_cm) : res.mu_h_low;

        double free_e = (n_donor > n_acceptor) ? (n_donor - n_acceptor) : 1e10;
        double free_h = (n_acceptor > n_donor) ? (n_acceptor - n_donor) : 1e10;

        res.conductivity = ELEMENTARY_CHARGE * (free_e * res.mu_e_field + free_h * res.mu_h_field);
        res.resistivity = (res.conductivity > 0.0) ? (1.0 / res.conductivity) : 1e18;

        return res;
    }

private:
    [[nodiscard]] static double calc_low_field_mobility(const CarrierParams& p, double temp_k, double n_total) {
        double temp_ratio = temp_k / 300.0;
        double mu_max_t = p.mu_max * std::pow(temp_ratio, -p.gamma);
        double mu_min_t = p.mu_min * std::pow(temp_ratio, -0.5);

        if (n_total <= 0.0) return mu_max_t;
        return mu_min_t + (mu_max_t - mu_min_t) / (1.0 + std::pow(n_total / p.n_ref, p.alpha));
    }

    [[nodiscard]] static double calc_drift_velocity(double mu_low, double e_field, double v_sat, double beta) {
        if (e_field <= 0.0) return 0.0;
        double term = (mu_low * e_field) / v_sat;
        return (mu_low * e_field) / std::pow(1.0 + std::pow(term, beta), 1.0 / beta);
    }

    Material material_;
    MaterialProfile profile_;
};

} // namespace physics::transport

int main() {
    using namespace physics::transport;

    std::cout << "=== ДВИГУН ОБЧИСЛЕННЯ РУХЛИВОСТІ НОСІЇВ (C++20) ===\n\n";

    MobilitySolver solver(Material::Silicon);
    constexpr double temp_k = 300.0;
    constexpr double electric_field = 5000.0;
    const std::vector<double> doping_levels = {1e14, 1e16, 1e18, 1e19};

    std::cout << "Матеріал: Кремній (Si), T = " << temp_k << " K, E = " << electric_field << " В/см\n";
    std::cout << std::string(80, '-') << "\n";
    std::cout << std::left << std::setw(14) << "Допування Nd" 
              << std::setw(14) << "μ_e (см²/Vs)" 
              << std::setw(14) << "μ_h (см²/Vs)" 
              << std::setw(18) << "v_drift_e (см/с)" 
              << std::setw(14) << "Опір (Ом·см)" << "\n";
    std::cout << std::string(80, '-') << "\n";

    for (double nd : doping_levels) {
        auto result = solver.solve(temp_k, nd, 0.0, electric_field);
        if (result) {
            std::cout << std::scientific << std::setprecision(1) << std::setw(14) << nd
                      << std::fixed << std::setprecision(1) << std::setw(14) << result->mu_e_field
                      << std::setw(14) << result->mu_h_field
                      << std::scientific << std::setprecision(2) << std::setw(18) << result->v_drift_e
                      << std::fixed << std::setprecision(4) << std::setw(14) << result->resistivity << "\n";
        }
    }

    return 0;
}
