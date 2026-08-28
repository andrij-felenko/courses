#include <vector>
#include <span>
#include <optional>
#include <numeric>
#include <stdexcept>
#include <cmath>

struct InductorAnalysisResult {
    double l_zero{0.0};        // Початкова індуктивність L_0, Гн
    double i_sat_10{0.0};      // Струм при спаді L на 10%, А
    double i_sat_20{0.0};      // Струм при спаді L на 20%, А
    double i_sat_30{0.0};      // Струм при спаді L на 30%, А
    double energy_max_j{0.0};  // Повна накопичена енергія магнітного поля, Дж
};

struct InductorWaveformCurves {
    std::vector<double> l_diff; // Диференціальна індуктивність L_diff(t)
    std::vector<double> psi;    // Потокозчеплення Psi(t)
};

class PulsedInductanceAnalyzer {
public:
    PulsedInductanceAnalyzer(double dt, double r_dc)
        : dt_(dt), r_dc_(r_dc) {
        if (dt <= 0.0) {
            throw std::invalid_argument("Time step dt must be positive");
        }
        if (r_dc < 0.0) {
            throw std::invalid_argument("Active resistance r_dc cannot be negative");
        }
    }

    [[nodiscard]] std::pair<InductorWaveformCurves, std::optional<InductorAnalysisResult>>
    analyze(std::span<const double> v_raw, std::span<const double> i_raw) const {
        const size_t n = v_raw.size();
        if (n < 10 || n != i_raw.size()) {
            return {{}, std::nullopt};
        }

        InductorWaveformCurves curves{
            .l_diff = std::vector<double>(n, 0.0),
            .psi = std::vector<double>(n, 0.0)
        };

        // 1. Чисельне інтегрування потокозчеплення Psi(t) та енергії
        double total_energy = 0.0;
        for (size_t k = 1; k < n; ++k) {
            const double e_prev = v_raw[k - 1] - i_raw[k - 1] * r_dc_;
            const double e_curr = v_raw[k] - i_raw[k] * r_dc_;
            const double d_psi = 0.5 * (e_prev + e_curr) * dt_;
            curves.psi[k] = curves.psi[k - 1] + d_psi;

            const double avg_i = 0.5 * (i_raw[k - 1] + i_raw[k]);
            total_energy += avg_i * d_psi;
        }

        // 2. 5-точковий фільтр Савицького-Голея для обчислення di/dt
        for (size_t k = 2; k < n - 2; ++k) {
            const double didt = (-2.0 * i_raw[k - 2] - 1.0 * i_raw[k - 1] +
                                  1.0 * i_raw[k + 1] + 2.0 * i_raw[k + 2]) / (10.0 * dt_);
            const double e_ind = v_raw[k] - i_raw[k] * r_dc_;

            if (didt > 1e2 && e_ind > 0.0) {
                curves.l_diff[k] = e_ind / didt;
            } else if (k > 2) {
                curves.l_diff[k] = curves.l_diff[k - 1];
            }
        }

        // 3. Базове усереднення L_0 по початковій ділянці
        const size_t start_idx = 2;
        size_t end_idx = std::max<size_t>(start_idx + 3, n / 7);
        if (end_idx >= n - 2) end_idx = n - 3;

        double l_sum = 0.0;
        size_t count = 0;
        for (size_t k = start_idx; k <= end_idx; ++k) {
            if (curves.l_diff[k] > 0.0) {
                l_sum += curves.l_diff[k];
                count++;
            }
        }

        if (count == 0) {
            return {std::move(curves), std::nullopt};
        }

        InductorAnalysisResult result{
            .l_zero = l_sum / static_cast<double>(count),
            .energy_max_j = total_energy
        };

        // 4. Детектування порогів спаду на 10%, 20%, 30%
        const double th_10 = result.l_zero * 0.90;
        const double th_20 = result.l_zero * 0.80;
        const double th_30 = result.l_zero * 0.70;

        bool f10 = false, f20 = false, f30 = false;
        for (size_t k = end_idx; k < n - 2; ++k) {
            if (!f10 && curves.l_diff[k] <= th_10 && curves.l_diff[k] > 0.0) {
                result.i_sat_10 = i_raw[k];
                f10 = true;
            }
            if (!f20 && curves.l_diff[k] <= th_20 && curves.l_diff[k] > 0.0) {
                result.i_sat_20 = i_raw[k];
                f20 = true;
            }
            if (!f30 && curves.l_diff[k] <= th_30 && curves.l_diff[k] > 0.0) {
                result.i_sat_30 = i_raw[k];
                f30 = true;
                break;
            }
        }

        if (!f10) {
            return {std::move(curves), std::nullopt};
        }

        return {std::move(curves), result};
    }

private:
    double dt_;
    double r_dc_;
};
