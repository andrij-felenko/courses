#include <iostream>
#include <cmath>
#include <array>
#include <utility>

struct CircuitParams {
    double v_cc{24.0};        // Напруга живлення, В
    double i_0{0.5};          // Початковий струм котушки, А
    double l_ind{0.08};       // Індуктивність навантаження, Гн
    double r_load{48.0};      // Власний опір обмотки, Ом
    double r_snubber{91.0};   // Опір снабера, Ом
    double c_snubber{10e-6};  // Ємність снабера, Ф
};

struct SimResult {
    double v_peak{0.0};
    double energy_res{0.0};
    double t_settle{0.0};
    bool arc_ignited{false};
};

class SnubberSimulator {
public:
    explicit SnubberSimulator(CircuitParams params) noexcept : params_{params} {}

    [[nodiscard]] SimResult run(double dt = 1e-7, double t_max = 5e-3) const noexcept {
        SimResult res{};
        double current_i = params_.i_0;
        double current_vc = 0.0;
        double t = 0.0;
        const double i_threshold = params_.i_0 * 0.01;
        bool settled = false;

        auto compute_derivs = [this](double i, double vc) noexcept -> std::pair<double, double> {
            double di = (params_.v_cc - vc - i * (params_.r_snubber + params_.r_load)) / params_.l_ind;
            double dvc = i / params_.c_snubber;
            return {di, dvc};
        };

        while (t < t_max) {
            const double v_sw = current_vc + current_i * params_.r_snubber;
            if (v_sw > res.v_peak) {
                res.v_peak = v_sw;
            }

            if (v_sw > 12.0 && current_i > 0.4) {
                res.arc_ignited = true;
            }

            res.energy_res += (current_i * current_i * params_.r_snubber) * dt;

            if (!settled && std::abs(current_i) < i_threshold) {
                res.t_settle = t;
                settled = true;
            }

            // Інтегрування RK4
            const auto [k1_i, k1_vc] = compute_derivs(current_i, current_vc);
            const auto [k2_i, k2_vc] = compute_derivs(current_i + 0.5 * dt * k1_i, current_vc + 0.5 * dt * k1_vc);
            const auto [k3_i, k3_vc] = compute_derivs(current_i + 0.5 * dt * k2_i, current_vc + 0.5 * dt * k2_vc);
            const auto [k4_i, k4_vc] = compute_derivs(current_i + dt * k3_i, current_vc + dt * k3_vc);

            current_i += (dt / 6.0) * (k1_i + 2.0 * k2_i + 2.0 * k3_i + k4_i);
            current_vc += (dt / 6.0) * (k1_vc + 2.0 * k2_vc + 2.0 * k3_vc + k4_vc);
            t += dt;
        }

        return res;
    }

private:
    CircuitParams params_;
};
