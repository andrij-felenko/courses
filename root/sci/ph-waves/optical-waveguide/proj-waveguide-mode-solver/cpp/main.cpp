#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>
#include <iomanip>

struct WaveguideMode {
    int index;
    bool is_even;
    double u;
    double h;
    double q;
    double beta;
    double n_eff;
};

class WaveguideSolver {
public:
    enum class Error {
        InvalidIndices,
        InvalidDimensions,
        NoSupportedModes
    };

    struct Params {
        double n1;
        double n2;
        double d_um;
        double lambda_um;
    };

    static std::expected<WaveguideSolver, Error> create(Params params) {
        if (params.n1 <= params.n2) {
            return std::unexpected(Error::InvalidIndices);
        }
        if (params.d_um <= 0.0 || params.lambda_um <= 0.0) {
            return std::unexpected(Error::InvalidDimensions);
        }
        return WaveguideSolver(params);
    }

    [[nodiscard]] double v_number() const noexcept { return v_num_; }
    [[nodiscard]] const std::vector<WaveguideMode>& modes() const noexcept { return modes_; }

private:
    explicit WaveguideSolver(Params params)
        : params_(params),
          k0_(2.0 * std::numbers::pi / params.lambda_um),
          v_num_(k0_ * params.d_um * std::sqrt(params.n1 * params.n1 - params.n2 * params.n2)) {
        solve_modes();
    }

    static double mode_residual(double u, double V, bool is_even) noexcept {
        const double w = std::sqrt((V * V / 4.0) - u * u);
        return is_even ? (u * std::tan(u) - w) : (-u * (1.0 / std::tan(u)) - w);
    }

    static double bisection(double low, double high, double V, bool is_even, double tol = 1e-10) noexcept {
        while ((high - low) > tol) {
            const double mid = 0.5 * (low + high);
            if (mode_residual(mid, V, is_even) * mode_residual(low, V, is_even) <= 0.0) {
                high = mid;
            } else {
                low = mid;
            }
        }
        return 0.5 * (low + high);
    }

    void solve_modes() {
        const int total_modes = static_cast<int>(std::floor(v_num_ / std::numbers::pi)) + 1;
        modes_.reserve(total_modes);

        for (int m = 0; m < total_modes; ++m) {
            const bool is_even = (m % 2 == 0);
            const double low = m * (std::numbers::pi / 2.0) + 1e-6;
            double high = (m + 1) * (std::numbers::pi / 2.0) - 1e-6;

            if (high > (v_num_ / 2.0)) {
                high = (v_num_ / 2.0) - 1e-6;
            }

            const double u = bisection(low, high, v_num_, is_even);
            const double h = 2.0 * u / params_.d_um;
            const double q = 2.0 * std::sqrt((v_num_ * v_num_ / 4.0) - u * u) / params_.d_um;
            const double beta = std::sqrt(k0_ * k0_ * params_.n1 * params_.n1 - h * h);

            modes_.push_back(WaveguideMode{
                .index = m,
                .is_even = is_even,
                .u = u,
                .h = h,
                .q = q,
                .beta = beta,
                .n_eff = beta / k0_
            });
        }
    }

    Params params_;
    double k0_;
    double v_num_;
    std::vector<WaveguideMode> modes_;
};

int main() {
    auto solver_result = WaveguideSolver::create({
        .n1 = 3.45,        // Кремній (Si)
        .n2 = 1.45,        // Оксид кремнію (SiO2)
        .d_um = 0.22,      // Товщина SOI пластини 220 нм
        .lambda_um = 1.55  // Довжина хвилі 1550 нм
    });

    if (!solver_result) {
        std::cerr << "Помилка ініціалізації хвилеводу!\n";
        return 1;
    }

    const auto& solver = *solver_result;
    std::cout << std::fixed << std::setprecision(5);
    std::cout << "=== Солвер нанофотонного хвилеводу SOI (C++23) ===\n";
    std::cout << "V-число: " << solver.v_number() << "\n\n";

    for (const auto& mode : solver.modes()) {
        std::cout << "Мода TE" << mode.index << " (" << (mode.is_even ? "Парна" : "Непарна") << "):\n"
                  << "  n_eff = " << mode.n_eff << "\n"
                  << "  beta  = " << mode.beta << " 1/мкм\n"
                  << "  h     = " << mode.h << " 1/мкм\n"
                  << "  q     = " << mode.q << " 1/мкм\n\n";
    }

    return 0;
}
