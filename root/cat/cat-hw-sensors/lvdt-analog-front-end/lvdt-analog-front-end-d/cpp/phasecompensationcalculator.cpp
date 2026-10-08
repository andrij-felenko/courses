#include <iostream>
#include <cmath>
#include <iomanip>

class PhaseCompensationCalculator {
public:
    static void compute(double freq_hz, double sensor_phase_deg, double c_farads) {
        double omega = 2.0 * M_PI * freq_hz;
        double phase_rad = sensor_phase_deg * (M_PI / 180.0);
        double r_ohm = std::tan(std::abs(phase_rad) / 2.0) / (omega * c_farads);
        double gain_loss_pct = (1.0 - std::cos(phase_rad)) * 100.0;

        std::cout << std::fixed << std::setprecision(2);
        std::cout << "=== Розрахунок фазової компенсації LVDT ===\n";
        std::cout << "Втрати сигналу без компенсації cos(phi): " << gain_loss_pct << "%\n";
        std::cout << "Розрахунковий опір R_comp: " << r_ohm << " Ом\n";
    }
};
