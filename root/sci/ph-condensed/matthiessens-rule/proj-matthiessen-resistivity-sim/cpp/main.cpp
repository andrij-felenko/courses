#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <iomanip>
#include <span >
#include <expected>

struct MetalProperties {
    std::string name;
    double theta_D;      // Температура Дебая, К
    double A_phonon;     // Амплітудний множник фононів, мкОм·см
    double rho_0;        // Залишковий опір на домішках, мкОм·см
};

struct TwoBandResult {
    double temp_k;
    double rho_total;
    double dmr_deviation;
};

class MatthiessenSimulator {
private:
    static double bloch_gruneisen_kernel(double z) noexcept {
        if (z < 1e-4) {
            return z * z * z;
        }
        double ez = std::exp(z);
        return (z * z * z * z * z) / ((ez - 1.0) * (1.0 - 1.0 / ez));
    }

    static double integrate_simpson(double x_max, std::size_t steps = 500) noexcept {
        if (x_max <= 0.0) return 0.0;
        if (steps % 2 != 0) steps++;

        double h = x_max / static_cast<double>(steps);
        double sum = bloch_gruneisen_kernel(0.0) + bloch_gruneisen_kernel(x_max);

        for (std::size_t i = 1; i < steps; ++i) {
            double z = static_cast<double>(i) * h;
            double weight = (i % 2 == 1) ? 4.0 : 2.0;
            sum += weight * bloch_gruneisen_kernel(z);
        }
        return (h / 3.0) * sum;
    }

public:
    static double calculate_phonon_resistivity(double temp_k, double theta_d, double a_coeff) noexcept {
        if (temp_k <= 1e-3) return 0.0;
        double x_max = theta_d / temp_k;
        double ratio = temp_k / theta_d;
        double integral = integrate_simpson(x_max);
        return a_coeff * std::pow(ratio, 5.0) * integral;
    }

    static double calculate_total_resistivity(const MetalProperties& metal, double temp_k) noexcept {
        return metal.rho_0 + calculate_phonon_resistivity(temp_k, metal.theta_D, metal.A_phonon);
    }

    static std::expected<double, std::string> calculate_rrr(const MetalProperties& metal) noexcept {
        double rho_4_2 = calculate_total_resistivity(metal, 4.2);
        if (rho_4_2 <= 0.0) {
            return std::unexpected("Залишковий опір не може бути нульовим або від'ємним");
        }
        double rho_293 = calculate_total_resistivity(metal, 293.15);
        return rho_293 / rho_4_2;
    }

    static TwoBandResult calculate_two_band_dmr(double temp_k, 
                                                 double rho_s0, double rho_d0, 
                                                 double a_s, double a_d, 
                                                 double theta_d) noexcept {
        double rho_sph = calculate_phonon_resistivity(temp_k, theta_d, a_s);
        double rho_dph = calculate_phonon_resistivity(temp_k, theta_d, a_d);

        double rho_s = rho_s0 + rho_sph;
        double rho_d = rho_d0 + rho_dph;

        double rho_tot = (rho_s * rho_d) / (rho_s + rho_d);

        double rho_0_tot = (rho_s0 * rho_d0) / (rho_s0 + rho_d0);
        double rho_ph_tot = (rho_sph * rho_dph) / (rho_sph + rho_dph);
        double rho_matthiessen = rho_0_tot + rho_ph_tot;

        return TwoBandResult{temp_k, rho_tot, rho_tot - rho_matthiessen};
    }
};

int main() {
    MetalProperties pure_cu{"Чиста мідь (OFHC 5N)", 343.0, 15.2, 0.0016};
    MetalProperties alloy_cu{"Сплав Cu-0.1%Ni", 343.0, 15.2, 0.1250};

    std::cout << "=== КВАНТОВО-КІНЕТИЧНЕ МОДЕЛЮВАННЯ ОПОРУ МЕТАЛІВ ===\n\n";

    const std::vector<double> temperatures{1.0, 4.2, 10.0, 20.0, 50.0, 100.0, 200.0, 293.15, 500.0};

    std::cout << std::left << std::setw(8)  << "T (K)"
              << " | " << std::setw(18) << "rho_pure (мкОм·см)"
              << " | " << std::setw(18) << "rho_alloy (мкОм·см)"
              << " | " << std::setw(16) << "Delta_rho" << "\n";
    std::cout << std::string(70, '-') << "\n";

    for (double t : temperatures) {
        double rho_p = MatthiessenSimulator::calculate_total_resistivity(pure_cu, t);
        double rho_a = MatthiessenSimulator::calculate_total_resistivity(alloy_cu, t);
        double delta = rho_a - rho_p;

        std::cout << std::fixed << std::setprecision(1) << std::setw(8) << t
                  << " | " << std::setprecision(6) << std::setw(18) << rho_p
                  << " | " << std::setprecision(6) << std::setw(18) << rho_a
                  << " | " << std::setprecision(6) << std::setw(16) << delta << "\n";
    }

    std::cout << std::string(70, '-') << "\n";

    if (auto rrr_pure = MatthiessenSimulator::calculate_rrr(pure_cu)) {
        std::cout << "RRR чистої міді: " << std::fixed << std::setprecision(1) << *rrr_pure << "\n";
    }
    if (auto rrr_alloy = MatthiessenSimulator::calculate_rrr(alloy_cu)) {
        std::cout << "RRR сплаву Cu-Ni: " << std::fixed << std::setprecision(2) << *rrr_alloy << "\n\n";
    }

    std::cout << "=== ДВОЗОННІ ВІДХИЛЕННЯ ВІД ПРАВИЛА МАТІССЕНА (DMR) ===\n";
    std::cout << std::left << std::setw(8) << "T (K)" 
              << " | " << std::setw(18) << "rho_total (мкОм·см)" 
              << " | " << std::setw(16) << "DMR Delta_rho" << "\n";
    std::cout << std::string(52, '-') << "\n";

    for (double t : temperatures) {
        auto res = MatthiessenSimulator::calculate_two_band_dmr(t, 0.05, 0.80, 12.0, 45.0, 240.0);
        std::cout << std::fixed << std::setprecision(1) << std::setw(8) << res.temp_k
                  << " | " << std::setprecision(6) << std::setw(18) << res.rho_total
                  << " | " << std::setprecision(6) << std::setw(16) << res.dmr_deviation << "\n";
    }

    return 0;
}
