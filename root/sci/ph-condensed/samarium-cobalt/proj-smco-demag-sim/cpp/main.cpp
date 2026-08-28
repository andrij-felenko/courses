#include <iostream>
#include <vector>
#include <cmath>
#include <expected>
#include <string_view>
#include <iomanip>

namespace smco {

constexpr double MU_0 = 1.2566370614359173e-6; // Гн/м

enum class DemagError {
    InvalidGeometry,
    AboveCurieTemperature
};

struct MagnetGrade {
    std::string_view name;
    double br_20c;    // Тл
    double hcj_20c;   // А/м
    double alpha_br;  // %/°C
    double beta_hcj;  // %/°C
    double mu_rec;
    double tc;        // °C
};

struct OperatingState {
    double B_d;       // Тл
    double H_d;       // А/м
    double load_line_slope; // P_c
    bool is_irreversible;
};

class DemagSimulator {
public:
    explicit DemagSimulator(MagnetGrade grade) : grade_(grade) {}

    [[nodiscard]] std::expected<OperatingState, DemagError>
    calculate_state(double temp_c, double demag_factor_nd) const {
        if (demag_factor_nd <= 0.0 || demag_factor_nd >= 1.0) {
            return std::unexpected(DemagError::InvalidGeometry);
        }
        if (temp_c >= grade_.tc) {
            return std::unexpected(DemagError::AboveCurieTemperature);
        }

        const double dT = temp_c - 20.0;
        const double br_t = std::max(0.0, grade_.br_20c * (1.0 + (grade_.alpha_br / 100.0) * dT));
        const double hcj_t = std::max(0.0, grade_.hcj_20c * (1.0 + (grade_.beta_hcj / 100.0) * dT));

        const double Pc = (1.0 - demag_factor_nd) / demag_factor_nd;
        const double H_d = - br_t / (MU_0 * (Pc + grade_.mu_rec));
        const double B_d = - MU_0 * Pc * H_d;

        const bool demagged = (std::abs(H_d) >= hcj_t);

        return OperatingState{
            .B_d = B_d,
            .H_d = H_d,
            .load_line_slope = Pc,
            .is_irreversible = demagged
        };
    }

private:
    MagnetGrade grade_;
};

} // namespace smco

int main() {
    using namespace smco;

    constexpr MagnetGrade Sm2Co17_HT{
        .name = "Sm2Co17 High-Temp Grade",
        .br_20c = 1.12,
        .hcj_20c = 1989400.0,
        .alpha_br = -0.032,
        .beta_hcj = -0.18,
        .mu_rec = 1.03,
        .tc = 820.0
    };

    DemagSimulator sim(Sm2Co17_HT);
    const double Nd = 0.25;

    std::cout << "=== Обчислення C++23 для " << Sm2Co17_HT.name << " (Nd = " << Nd << ") ===\n";
    std::cout << std::fixed << std::setprecision(3);

    const std::vector<double> test_temperatures = { 20.0, 200.0, 350.0, 500.0, 850.0 };

    for (double T : test_temperatures) {
        auto result = sim.calculate_state(T, Nd);
        std::cout << "Т = " << std::setw(5) << T << " °C: ";
        if (result) {
            std::cout << "B_d = " << result->B_d << " Тл, H_d = " 
                      << std::setw(8) << result->H_d / 1000.0 << " кА/м | "
                      << (result->is_irreversible ? "УВАГА: Незворотні втрати!" : "Норма");
        } else {
            if (result.error() == DemagError::AboveCurieTemperature) {
                std::cout << "ПОМИЛКА: Температура перевищує точку Кюрі!";
            } else {
                std::cout << "ПОМИЛКА: Некоректна геометрія (Nd)!";
            }
        }
        std::cout << '\n';
    }

    return 0;
}
