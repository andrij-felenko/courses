#include <iostream>
#include <memory>
#include <expected>
#include <span>
#include <cmath>
#include <numbers>

namespace denjoy {

class CircleMapSystem {
public:
    using LiftFn = double(*)(double, void*);
    using PrimeFn = double(*)(double, void*);

    CircleMapSystem(LiftFn lift, PrimeFn prime, void* user_data = nullptr) {
        config_.lift = lift;
        config_.prime = prime;
        config_.user_data = user_data;
        config_.period = 1.0;
    }

    [[nodiscard]] std::expected<double, denjoy_status_t>
    compute_rotation_number(long iterations = 500000L) const noexcept {
        denjoy_rotation_info_t info{};
        auto status = denjoy_compute_rotation_number(&config_, 0.0, iterations, &info);
        if (status != DENJOY_OK) {
            return std::unexpected(status);
        }
        return info.rotation_number;
    }

    [[nodiscard]] std::expected<denjoy_distortion_stats_t, denjoy_status_t>
    analyze_distortion(long q_step, int num_samples = 2000) const noexcept {
        denjoy_distortion_stats_t stats{};
        auto status = denjoy_check_distortion(&config_, q_step, num_samples, &stats);
        if (status != DENJOY_OK) {
            return std::unexpected(status);
        }
        return stats;
    }

private:
    denjoy_map_config_t config_{};
};

} // namespace denjoy

int main() {
    struct Params { double omega; double k; } params{ (std::numbers::sqrt5 - 1.0) / 2.0, 0.35 };

    auto lift = [](double x, void* ptr) -> double {
        auto* p = static_cast<Params*>(ptr);
        return x + p->omega - (p->k / (2.0 * std::numbers::pi)) * std::sin(2.0 * std::numbers::pi * x);
    };

    auto prime = [](double x, void* ptr) -> double {
        auto* p = static_cast<Params*>(ptr);
        return 1.0 - p->k * std::cos(2.0 * std::numbers::pi * x);
    };

    denjoy::CircleMapSystem system(lift, prime, &params);

    if (auto rot = system.compute_rotation_number(); rot) {
        std::cout << "C++20: Число обертання rho = " << *rot << "\n";
    }

    if (auto dist = system.analyze_distortion(987); dist) {
        std::cout << "C++20: Логарифмічне спотворення при q=987: " << dist->log_distortion << "\n";
    }

    return 0;
}
