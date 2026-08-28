#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>

class CasimirCalculator {
public:
    static constexpr double hbar = 1.054571817e-34; // Зменшена стала Планка (Дж·с)
    static constexpr double c    = 299792458.0;        // Швидкість світла у вакуумі (м/с)
    static constexpr double atm  = 1.01325e5;          // 1 атмосфера у Паскалях

    // Розрахунок ідеального тиску Казимира у Паскалях (Н/м²)
    static double idealPressure(double d_meters) {
        constexpr double pi = 3.14159265358979323846;
        double factor = (pi * pi) * hbar * c / 240.0;
        return - factor / (d_meters * d_meters * d_meters * d_meters);
    }

    // Розрахунок коефіцієнта поправки Ліфшиця для золота (Au)
    static double lifshitzFactor(double d_meters, double plasma_wave_nm = 136.0) {
        double lambda_p = plasma_wave_nm * 1e-9;
        return 1.0 / (1.0 + 1.2 * (lambda_p / d_meters));
    }
};

int main() {
    std::vector<double> distances_nm = {10.0, 20.0, 50.0, 100.0, 200.0, 500.0, 1000.0, 5000.0};

    std::cout << std::setw(8) << "d (nm)" << " | "
              << std::setw(14) << "P_ideal (Pa)" << " | "
              << std::setw(14) << "P_real (Pa)" << " | "
              << std::setw(14) << "P_real (atm)" << " | "
              << std::setw(10) << "Factor η" << "\n";
    std::cout << std::string(72, '-') << "\n";

    for (double d_nm : distances_nm) {
        double d_m = d_nm * 1e-9;
        double p_ideal = std::abs(CasimirCalculator::idealPressure(d_m));
        double eta = CasimirCalculator::lifshitzFactor(d_m);
        double p_real = p_ideal * eta;
        double p_real_atm = p_real / CasimirCalculator::atm;

        std::cout << std::scientific << std::setprecision(4)
                  << std::setw(8) << d_nm << " | "
                  << std::setw(14) << p_ideal << " | "
                  << std::setw(14) << p_real << " | "
                  << std::setw(14) << p_real_atm << " | "
                  << std::fixed << std::setprecision(4)
                  << std::setw(10) << eta << "\n";
    }

    return 0;
}
