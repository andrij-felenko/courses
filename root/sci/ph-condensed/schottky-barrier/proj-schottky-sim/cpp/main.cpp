#include <iostream>
#include <vector>
#include <cmath>
#include <expected>
#include <numeric>
#include <span>

namespace physics::schottky {

constexpr double Q_ELEM = 1.602176634e-19;
constexpr double K_BOLTZ = 1.380649e-23;
constexpr double EPS_0 = 8.8541878128e-14;

struct DeviceConfig {
    double area_cm2 = 1.0e-3;
    double rel_perm = 11.7;
    double richardson_a = 112.0;
};

struct CvFitResult {
    double nd_cm3;
    double v_bi_v;
    double slope;
};

enum class SimError {
    InvalidData,
    ConvergenceFailed
};

class SchottkySolver {
public:
    explicit SchottkySolver(DeviceConfig config) : cfg_(config) {}

    [[nodiscard]] double saturation_current(double phi_bn_ev, double temp_k) const noexcept {
        const double vt = (K_BOLTZ * temp_k) / Q_ELEM;
        return cfg_.area_cm2 * cfg_.richardson_a * (temp_k * temp_k) * std::exp(-phi_bn_ev / vt);
    }

    [[nodiscard]] std::expected<std::pair<std::vector<double>, std::vector<double>>, SimError>
    simulate_iv(double phi_bn_ev, double eta, double rs_ohm, double temp_k, double v_max, std::size_t steps) const {
        if (steps < 2 || v_max <= 0.0) return std::unexpected(SimError::InvalidData);

        std::vector<double> voltages(steps);
        std::vector<double> currents(steps);

        const double vt = (K_BOLTZ * temp_k) / Q_ELEM;
        const double is_sat = saturation_current(phi_bn_ev, temp_k);
        const double v_step = v_max / static_cast<double>(steps - 1);

        for (std::size_t idx = 0; idx < steps; ++idx) {
            const double v_ext = static_cast<double>(idx) * v_step;
            double curr = 1.0e-9;

            bool converged = false;
            for (int iter = 0; iter < 35; ++iter) {
                const double v_diode = v_ext - curr * rs_ohm;
                const double exp_term = std::exp(v_diode / (eta * vt));
                const double f_val = curr - is_sat * (exp_term - 1.0);
                const double df_val = 1.0 + is_sat * (rs_ohm / (eta * vt)) * exp_term;
                const double step = f_val / df_val;
                curr -= step;
                if (std::abs(step) < 1.0e-12) {
                    converged = true;
                    break;
                }
            }
            if (!converged) return std::unexpected(SimError::ConvergenceFailed);

            voltages[idx] = v_ext;
            currents[idx] = std::max(curr, 0.0);
        }

        return std::make_pair(std::move(voltages), std::move(currents));
    }

    [[nodiscard]] std::expected<CvFitResult, SimError>
    extract_cv(std::span<const double> vr, std::span<const double> c_pf, double temp_k) const {
        if (vr.size() != c_pf.size() || vr.size() < 2) return std::unexpected(SimError::InvalidData);

        const std::size_t n = vr.size();
        double sum_x = 0.0, sum_y = 0.0, sum_xy = 0.0, sum_xx = 0.0;

        for (std::size_t idx = 0; idx < n; ++idx) {
            const double c_farad = c_pf[idx] * 1.0e-12;
            const double y_val = 1.0 / (c_farad * c_farad);
            const double x_val = vr[idx];

            sum_x += x_val;
            sum_y += y_val;
            sum_xy += x_val * y_val;
            sum_xx += x_val * x_val;
        }

        const double count = static_cast<double>(n);
        const double slope = (count * sum_xy - sum_x * sum_y) / (count * sum_xx - sum_x * sum_x);
        const double intercept = (sum_y - slope * sum_x) / count;

        const double eps_s = cfg_.rel_perm * EPS_0;
        const double vt = (K_BOLTZ * temp_k) / Q_ELEM;

        CvFitResult res;
        res.slope = slope;
        res.nd_cm3 = 2.0 / (Q_ELEM * eps_s * (cfg_.area_cm2 * cfg_.area_cm2) * slope);
        res.v_bi_v = (intercept / slope) + vt;

        return res;
    }

private:
    DeviceConfig cfg_;
};

} // namespace physics::schottky

int main() {
    using namespace physics::schottky;
    SchottkySolver solver(DeviceConfig{.area_cm2 = 1.0e-3, .rel_perm = 11.7, .richardson_a = 112.0});

    auto res = solver.simulate_iv(0.70, 1.04, 15.0, 300.0, 0.6, 50);
    if (res) {
        const auto& [v, i] = *res;
        std::cout << "C++23 симуляцію пройдено. Точок: " << v.size() 
                  << ", Макс струм: " << i.back() * 1e3 << " мА\n";
    }
    return 0;
}
