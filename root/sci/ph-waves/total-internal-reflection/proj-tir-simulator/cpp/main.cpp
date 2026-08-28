#include <iostream>
#include <iomanip>
#include <cmath>
#include <vector>
#include <numbers>
#include <expected>
#include <string>

struct TirConfig {
    double n1{1.50};
    double n2{1.00};
    double n3{1.50};
    double lambda_nm{632.8};
    double theta_deg{45.0};
};

struct FtirPoint {
    double gap_nm;
    double gap_relative;
    double transmission;
    double reflection;
};

class FtirSimulator {
public:
    explicit FtirSimulator(TirConfig config) : config_(config) {}

    [[nodiscard]] std::expected<double, std::string> penetrationDepth() const {
        const double theta_rad = config_.theta_deg * std::numbers::pi / 180.0;
        const double sin_t = std::sin(theta_rad);
        const double val = config_.n1 * config_.n1 * sin_t * sin_t - config_.n2 * config_.n2;
        if (val <= 0.0) {
            return std::unexpected("Кут падіння менший за критичний!");
        }
        const double alpha = (2.0 * std::numbers::pi / config_.lambda_nm) * std::sqrt(val);
        return 1.0 / alpha;
    }

    [[nodiscard]] double transmission(double gap_nm) const {
        if (gap_nm <= 1e-9) return 1.0;

        const double theta_rad = config_.theta_deg * std::numbers::pi / 180.0;
        const double sin_t = std::sin(theta_rad);
        const double cos_t = std::cos(theta_rad);

        const double val = config_.n1 * config_.n1 * sin_t * sin_t - config_.n2 * config_.n2;
        if (val <= 0.0) return 1.0;

        const double alpha = (2.0 * std::numbers::pi / config_.lambda_nm) * std::sqrt(val);
        const double num = std::pow(config_.n1 * config_.n1 - config_.n2 * config_.n2, 2);
        const double den = 4.0 * config_.n1 * config_.n1 * val * cos_t * cos_t;
        const double C = num / den;

        const double arg = alpha * gap_nm;
        if (arg > 35.0) {
            return (4.0 / C) * std::exp(-2.0 * arg);
        }

        const double sh_val = std::sinh(arg);
        return 1.0 / (1.0 + C * sh_val * sh_val);
    }

    [[nodiscard]] std::vector<FtirPoint> scanGap(double max_gap_nm, std::size_t steps) const {
        std::vector<FtirPoint> results;
        results.reserve(steps + 1);

        for (std::size_t i = 0; i <= steps; ++i) {
            const double gap = i * (max_gap_nm / steps);
            const double T = transmission(gap);
            results.push_back({
                .gap_nm = gap,
                .gap_relative = gap / config_.lambda_nm,
                .transmission = T,
                .reflection = 1.0 - T
            });
        }
        return results;
    }

private:
    TirConfig config_;
};

int main() {
    TirConfig cfg{.n1 = 1.50, .n2 = 1.00, .n3 = 1.50, .lambda_nm = 632.8, .theta_deg = 45.0};
    FtirSimulator sim(cfg);

    auto dp_res = sim.penetrationDepth();
    if (!dp_res) {
        std::cerr << "Помилка: " << dp_res.error() << "\n";
        return 1;
    }

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Глибина проникнення dp = " << *dp_res << " nm\n\n";
    std::cout << std::setw(14) << "Зазор (nm)" 
              << std::setw(16) << "d / lambda" 
              << std::setw(18) << "Пропускання T"
              << std::setw(18) << "Відбиття R\n";
    std::cout << "------------------------------------------------------------------\n";

    auto table = sim.scanGap(cfg.lambda_nm * 3.0, 12);
    for (const auto& pt : table) {
        std::cout << std::setw(14) << pt.gap_nm 
                  << std::setw(16) << pt.gap_relative 
                  << std::setw(18) << std::setprecision(6) << pt.transmission 
                  << std::setw(18) << pt.reflection << "\n";
    }

    return 0;
}
