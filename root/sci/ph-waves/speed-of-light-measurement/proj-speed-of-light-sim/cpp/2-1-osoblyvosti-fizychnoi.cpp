#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>

struct MichelsonParams {
    double distance_m{35373.7};
    double nominal_freq_hz{528.25};
    int num_facets{8};
    double c_target{299792458.0};
};

class MichelsonAnalyzer {
public:
    explicit MichelsonAnalyzer(MichelsonParams p) : p_(p) {}

    [[nodiscard]] double sync_frequency() const noexcept {
        return p_.c_target / (2.0 * static_cast<double>(p_.num_facets) * p_.distance_m);
    }

    [[nodiscard]] double angular_deflection(double freq_hz) const noexcept {
        const double t_flight = 2.0 * p_.distance_m / p_.c_target;
        const double facet_angle = 2.0 * std::numbers::pi / static_cast<double>(p_.num_facets);
        const double rot_angle = 2.0 * std::numbers::pi * freq_hz * t_flight;
        return 2.0 * (rot_angle - facet_angle);
    }

    [[nodiscard]] double compute_speed(double freq_hz) const noexcept {
        return 2.0 * static_cast<double>(p_.num_facets) * freq_hz * p_.distance_m;
    }

private:
    MichelsonParams p_;
};

int main() {
    MichelsonParams setup{.distance_m = 35373.7, .nominal_freq_hz = 528.25, .num_facets = 8};
    MichelsonAnalyzer analyzer(setup);

    const double f_sync = analyzer.sync_frequency();
    std::cout << "=== Параметричний аналіз призми Майкельсона (C++) ===\n";
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Розрахункова синхронна частота: " << f_sync << " Гц\n\n";

    for (double df = -1.0; df <= 1.0; df += 0.25) {
        const double f_curr = f_sync + df;
        const double defl_mrad = analyzer.angular_deflection(f_curr) * 1000.0;
        const double c_est = analyzer.compute_speed(f_curr);
        const double err = std::abs(c_est - setup.c_target);

        std::cout << "f: " << f_curr << " Гц | Зсув: " << defl_mrad 
                  << " мрад | c: " << (c_est / 1000.0) << " км/с | Помилка: " << err << " м/с\n";
    }

    return 0;
}
