#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <algorithm>

// Фізичні параметри гетероструктури FM/AFM у системі СГС
struct MagneticStackParams {
    double Ms = 800.0;       // Намагніченість насичення FM (emu/cm³)
    double t_FM = 5.0e-7;    // Товщина FM шару (5 нм = 5e-7 см)
    double K_FM = 1.0e4;     // Одноосьова анізотропія FM (erg/cm³)
    double J_EB = 0.15;      // Енергія обмінного зв'язку інтерфейсу (erg/cm²)
    double phi_AFM = 0.0;    // Кут закріплених спінів AFM (радіани)
    double psi_field = 0.0;  // Кут прикладання зовнішнього поля (радіани)
};

// Структура для збереження точок розрахованої петлі
struct HysteresisPoint {
    double H_ext;            // Зовнішнє магнітне поле (Oe)
    double M_proj;           // Нормована намагніченість M / Ms
    double theta_eq;         // Рівноважний кут намагніченості (рад)
};

class ExchangeBiasSimulator {
public:
    explicit ExchangeBiasSimulator(MagneticStackParams params) : p_(params) {}

    // Повна магнітна енергія одиниці площі плівки (erg/cm²)
    [[nodiscard]] double compute_energy(double theta, double H_ext) const {
        double E_zeeman = -H_ext * p_.Ms * p_.t_FM * std::cos(theta - p_.psi_field);
        double E_anis = p_.K_FM * p_.t_FM * std::pow(std::sin(theta), 2.0);
        double E_exch = -p_.J_EB * std::cos(theta - p_.phi_AFM);
        return E_zeeman + E_anis + E_exch;
    }

    // Теоретичний розрахунок поля зміщення за формулою Мейклджона — Біна
    [[nodiscard]] double theoretical_HEB() const {
        return p_.J_EB / (p_.Ms * p_.t_FM);
    }

    // Пошук рівноважного кута методом дихотомії та локального сканування
    [[nodiscard]] double find_equilibrium_angle(double H_ext, double initial_theta) const {
        double best_theta = initial_theta;
        double min_energy = compute_energy(initial_theta, H_ext);

        constexpr double TWO_PI = 2.0 * M_PI;

        // Пошук локального мінімуму у вікні ±90 градусів від поточного стану
        for (int i = -90; i <= 90; ++i) {
            double test_theta = initial_theta + (i * M_PI / 180.0);
            
            // Приведення кута до діапазону [0, 2π)
            while (test_theta < 0.0) test_theta += TWO_PI;
            while (test_theta >= TWO_PI) test_theta -= TWO_PI;

            double energy = compute_energy(test_theta, H_ext);
            if (energy < min_energy) {
                min_energy = energy;
                best_theta = test_theta;
            }
        }
        return best_theta;
    }

    // Симуляція повного гістерезисного циклу
    [[nodiscard]] std::vector<HysteresisPoint> run_simulation(double H_max, int steps) const {
        std::vector<HysteresisPoint> loop;
        loop.reserve(static_cast<size_t>((steps + 1) * 2));

        double delta_H = (2.0 * H_max) / steps;
        double current_theta = p_.psi_field; // Насичення у додатному полі

        // 1. Зворотний хід: +H_max -> -H_max
        for (int i = 0; i <= steps; ++i) {
            double H = H_max - i * delta_H;
            current_theta = find_equilibrium_angle(H, current_theta);
            double m_proj = std::cos(current_theta - p_.psi_field);
            loop.push_back({H, m_proj, current_theta});
        }

        // 2. Прямий хід: -H_max -> +H_max
        for (int i = 0; i <= steps; ++i) {
            double H = -H_max + i * delta_H;
            current_theta = find_equilibrium_angle(H, current_theta);
            double m_proj = std::cos(current_theta - p_.psi_field);
            loop.push_back({H, m_proj, current_theta});
        }

        return loop;
    }

private:
    MagneticStackParams p_;
};

int main() {
    MagneticStackParams params;
    ExchangeBiasSimulator sim(params);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== МОДЕЛЮВАННЯ ПЕТЛІ ГІСТЕРЕЗИСУ FM/AFM ===\n";
    std::cout << "Параметри: Ms = " << params.Ms << " emu/cm³, t_FM = " << params.t_FM * 1.0e7 << " nm\n";
    std::cout << "Теоретичне поле обмінного зміщення H_EB: " << sim.theoretical_HEB() << " Oe\n\n";

    constexpr double H_MAX = 800.0;
    constexpr int FIELD_STEPS = 80;
    auto loop_data = sim.run_simulation(H_MAX, FIELD_STEPS);

    std::cout << "--- Зріз результатів розрахунку (перші 12 точок) ---\n";
    std::cout << "  H (Oe)    |   M / Ms   |   Theta (град)\n";
    std::cout << "------------+------------+----------------\n";

    for (size_t i = 0; i < std::min<size_t>(12, loop_data.size()); ++i) {
        const auto& pt = loop_data[i];
        std::cout << std::setw(9) << pt.H_ext << "   |   "
                  << std::setw(8) << pt.M_proj << " |   "
                  << std::setw(9) << (pt.theta_eq * 180.0 / M_PI) << "\n";
    }

    return 0;
}
