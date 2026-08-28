#include <iostream>
#include <vector>
#include <cmath>
#include <optional>
#include <span >
#include <algorithm>

namespace boundary_layer {

struct FlowPoint {
    double x{0.0};
    double U_e{0.0};
    double dUe_dx{0.0};
};

struct BoundaryLayerResult {
    double x{0.0};
    double U_e{0.0};
    double theta{0.0};
    double delta_star{0.0};
    double H{2.59};
    double lambda_T{0.0};
    double C_f{0.0};
    bool is_separated{false};
};

class ThwaitesSolver {
public:
    explicit ThwaitesSolver(double kinematic_viscosity) 
        : nu_(kinematic_viscosity) {}

    [[nodiscard]] std::vector<BoundaryLayerResult> solve(std::span<const FlowPoint> points) const {
        if (points.size() < 2 || nu_ <= 0.0) {
            return {};
        }

        std::vector<BoundaryLayerResult> results;
        results.reserve(points.size());

        double integral_val = 0.0;

        // Початкова точка
        const auto& p0 = points[0];
        BoundaryLayerResult r0;
        r0.x = p0.x;
        r0.U_e = p0.U_e;

        if (p0.U_e < 1e-9) {
            r0.lambda_T = 0.075;
            auto [l_val, H_val] = evaluate_correlations(0.075);
            r0.theta = std::sqrt(0.075 * nu_ / (p0.dUe_dx > 1e-9 ? p0.dUe_dx : 1.0));
            r0.H = H_val;
            r0.delta_star = r0.theta * H_val;
            r0.C_f = 0.0;
        } else {
            r0.theta = 1e-6;
            r0.lambda_T = (r0.theta * r0.theta / nu_) * p0.dUe_dx;
            auto [l_val, H_val] = evaluate_correlations(r0.lambda_T);
            r0.H = H_val;
            r0.delta_star = r0.theta * H_val;
            r0.C_f = 2.0 * nu_ * l_val / (p0.U_e * r0.theta);
        }
        results.push_back(r0);

        // Чисельне інтегрування за методом Твейтса
        for (size_t i = 1; i < points.size(); ++i) {
            const auto& p_prev = points[i - 1];
            const auto& p_curr = points[i];

            double dx = p_curr.x - p_prev.x;
            double u_prev_5 = std::pow(p_prev.U_e, 5.0);
            double u_curr_5 = std::pow(p_curr.U_e, 5.0);

            integral_val += 0.5 * (u_prev_5 + u_curr_5) * dx;

            double u_curr_6 = std::max(std::pow(p_curr.U_e, 6.0), 1e-12);
            double theta_sq = (0.45 * nu_ / u_curr_6) * integral_val;

            BoundaryLayerResult r;
            r.x = p_curr.x;
            r.U_e = p_curr.U_e;
            r.theta = std::sqrt(theta_sq);
            r.lambda_T = (theta_sq / nu_) * p_curr.dUe_dx;

            if (r.lambda_T <= -0.09) {
                r.is_separated = true;
                r.H = 3.55;
                r.delta_star = r.theta * 3.55;
                r.C_f = 0.0;
            } else {
                auto [l_val, H_val] = evaluate_correlations(r.lambda_T);
                r.H = H_val;
                r.delta_star = r.theta * H_val;
                r.C_f = 2.0 * nu_ * l_val / (p_curr.U_e * r.theta);
            }

            results.push_back(r);
        }

        return results;
    }

private:
    struct CorrelationResult {
        double l;
        double H;
    };

    [[nodiscard]] static constexpr CorrelationResult evaluate_correlations(double lambda) noexcept {
        if (lambda <= -0.09) {
            return {0.0, 3.55};
        }
        if (lambda <= 0.0) {
            return {
                0.225 + 2.3 * lambda - 6.0 * lambda * lambda,
                2.61 - 3.75 * lambda + 80.0 * lambda * lambda
            };
        }
        return {
            0.225 + 2.3 * lambda - 2.0 * lambda * lambda,
            2.61 - 3.75 * lambda + 15.0 * lambda * lambda
        };
    }

    double nu_;
};

} // namespace boundary_layer
