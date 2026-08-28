#include <iostream>
#include <vector>
#include <span>
#include <optional>
#include <numeric>
#include <cmath>
#include <iomanip>

struct TlmResult {
    double r_sh_ohm_sq;   // Шаровий опір [Ом/кв]
    double r_c_ohm;        // Опір одного контакту [Ом]
    double l_t_um;         // Довжина перенесення [мкм]
    double rho_c_ohm_cm2;  // Питомий опір контакту [Ом·см²]
    double r2_score;       // Коефіцієнт детермінації R^2
    double l_ratio;        // Співвідношення L / L_T
};

class TlmAnalyzer {
public:
    constexpr TlmAnalyzer(double width_um, double length_um) noexcept
        : w_cm_(width_um * 1e-4), l_cm_(length_um * 1e-4) {}

    [[nodiscard]] std::optional<TlmResult> analyze(
        std::span<const double> spacings_um,
        std::span<const double> resistances_ohm) const {

        if (spacings_um.size() != resistances_ohm.size() || spacings_um.size() < 2) {
            return std::nullopt;
        }

        const auto n = static_cast<double>(spacings_um.size());
        double sum_x = 0.0, sum_y = 0.0, sum_xx = 0.0, sum_xy = 0.0;

        for (size_t i = 0; i < spacings_um.size(); ++i) {
            const double x = spacings_um[i] * 1e-4; // мкм -> см
            const double y = resistances_ohm[i];
            sum_x += x;
            sum_y += y;
            sum_xx += x * x;
            sum_xy += x * y;
        }

        const double denom = n * sum_xx - sum_x * sum_x;
        if (std::abs(denom) < 1e-15) {
            return std::nullopt;
        }

        const double slope = (n * sum_xy - sum_x * sum_y) / denom;
        const double intercept = (sum_y * sum_xx - sum_x * sum_xy) / denom;

        if (slope <= 0.0 || intercept <= 0.0) {
            return std::nullopt;
        }

        TlmResult res{};
        res.r_sh_ohm_sq = slope * w_cm_;
        res.r_c_ohm = intercept / 2.0;
        const double l_t_cm = intercept / (2.0 * slope);
        res.l_t_um = l_t_cm * 1e4;
        res.l_ratio = l_cm_ / l_t_cm;

        if (res.l_ratio < 2.0) {
            res.rho_c_ohm_cm2 = res.r_c_ohm * w_cm_ * l_t_cm * std::tanh(res.l_ratio);
        } else {
            res.rho_c_ohm_cm2 = res.r_c_ohm * w_cm_ * l_t_cm;
        }

        const double y_mean = sum_y / n;
        double ss_tot = 0.0, ss_res = 0.0;
        for (size_t i = 0; i < spacings_um.size(); ++i) {
            const double x = spacings_um[i] * 1e-4;
            const double y = resistances_ohm[i];
            const double y_pred = slope * x + intercept;
            ss_tot += (y - y_mean) * (y - y_mean);
            ss_res += (y - y_pred) * (y - y_pred);
        }

        res.r2_score = (ss_tot > 0.0) ? (1.0 - ss_res / ss_tot) : 0.0;
        return res;
    }

private:
    double w_cm_;
    double l_cm_;
};

int main() {
    TlmAnalyzer analyzer(100.0, 20.0);
    std::vector<double> d_um{5.0, 10.0, 15.0, 20.0, 25.0};
    std::vector<double> r_ohm{12.4, 18.2, 24.1, 30.0, 35.9};

    if (const auto res = analyzer.analyze(d_um, r_ohm)) {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "R_sh    = " << res->r_sh_ohm_sq << " Ohm/sq\n";
        std::cout << "R_c     = " << std::setprecision(3) << res->r_c_ohm << " Ohm\n";
        std::cout << "L_T     = " << res->l_t_um << " um\n";
        std::cout << "rho_c   = " << std::scientific << res->rho_c_ohm_cm2 << " Ohm*cm^2\n";
        std::cout << "R^2     = " << std::fixed << std::setprecision(4) << res->r2_score << "\n";
        std::cout << "L / L_T = " << res->l_ratio << "\n";
    }
    return 0;
}
