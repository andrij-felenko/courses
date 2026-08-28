#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <memory>
#include <string>

// Фізичні константи та параметри феромагнітного матеріалу
struct MaterialProperties {
    std::string name = "Cobalt (Co)";
    double K1 = 4.5e5;               // Константа одноосної анізотропії (Дж/м³)
    double Ms = 1.4e6;               // Намагніченість насичення (А/м)
    double mu0 = 4.0 * M_PI * 1e-7;   // Магнітна стала (Гн/м)

    // Обчислення ефективного поля анізотропії HA
    double anisotropy_field() const {
        return (2.0 * K1) / (mu0 * Ms);
    }
};

// Результат обчислення однієї точки петлі гістерезису
struct LoopPoint {
    double h_applied;      // Зовнішнє поле h = H / HA
    double m_parallel;     // Поздовжня проекція m_parallel
    double m_perpendicular;// Поперечна проекція m_perp
    double theta;          // Кут намагніченості (рад)
};

// Клас мікромагнітного симулятора (RAII та інкапсуляція)
class AnisotropySimulator {
private:
    MaterialProperties mat_;

public:
    explicit AnisotropySimulator(MaterialProperties mat) : mat_(std::move(mat)) {}

    // Густина безрозмірної енергії e(θ)
    double energy_density(double theta, double hx, double hz) const {
        return 0.5 * std::pow(std::sin(theta), 2) - hz * std::cos(theta) - hx * std::sin(theta);
    }

    // Перша похідна de/dθ
    double d_energy(double theta, double hx, double hz) const {
        return std::sin(theta) * std::cos(theta) + hz * std::sin(theta) - hx * std::cos(theta);
    }

    // Друга похідна d²e/dθ² (перевірка стійкості)
    double d2_energy(double theta, double hx, double hz) const {
        return std::cos(2.0 * theta) + hz * std::cos(theta) + hx * std::sin(theta);
    }

    // Гібридний розв'язувач для пошуку стійкого мінімуму
    double solve_equilibrium(double initial_theta, double hx, double hz) const {
        double theta = initial_theta;
        const int max_newton_iter = 60;
        const double tol = 1e-8;

        // Фаза 1: Метод Ньютона — Рафсона
        for (int iter = 0; iter < max_newton_iter; ++iter) {
            double g = d_energy(theta, hx, hz);
            double h = d2_energy(theta, hx, hz);

            if (std::abs(g) < tol && h > 0.0) {
                return theta; // Успішно знайдено стійкий мінімум
            }

            if (std::abs(h) < 1e-12) {
                h = (h >= 0) ? 1e-6 : -1e-6;
            }

            theta -= g / h;
        }

        // Фаза 2: Сканування по дискретній сітці при провалі Ньютона
        const int grid_steps = 720;
        double min_e = 1e18;
        double best_theta = initial_theta;

        for (int i = 0; i < grid_steps; ++i) {
            double t = i * 2.0 * M_PI / grid_steps;
            if (d2_energy(t, hx, hz) > 0.0) {
                double e_val = energy_density(t, hx, hz);
                if (e_val < min_e) {
                    min_e = e_val;
                    best_theta = t;
                }
            }
        }
        return best_theta;
    }

    // Симуляція повного циклу гістерезисної петлі для кута theta_H
    std::vector<LoopPoint> run_hysteresis_loop(double theta_H_deg, int steps = 200) const {
        std::vector<LoopPoint> loop;
        loop.reserve(steps * 2 + 2);

        double theta_H = theta_H_deg * M_PI / 180.0;
        double current_theta = (std::cos(theta_H) >= 0.0) ? 0.0 : M_PI;

        const double h_max = 2.0;

        // Пряма гілка поля: від +h_max до -h_max
        for (int i = 0; i <= steps; ++i) {
            double h_val = h_max - (2.0 * h_max * i / steps);
            double hx = h_val * std::sin(theta_H);
            double hz = h_val * std::cos(theta_H);

            current_theta = solve_equilibrium(current_theta, hx, hz);
            double m_par = std::cos(current_theta - theta_H);
            double m_perp = std::sin(current_theta - theta_H);

            loop.push_back({h_val, m_par, m_perp, current_theta});
        }

        // Зворотна гілка поля: від -h_max до +h_max
        for (int i = 0; i <= steps; ++i) {
            double h_val = -h_max + (2.0 * h_max * i / steps);
            double hx = h_val * std::sin(theta_H);
            double hz = h_val * std::cos(theta_H);

            current_theta = solve_equilibrium(current_theta, hx, hz);
            double m_par = std::cos(current_theta - theta_H);
            double m_perp = std::sin(current_theta - theta_H);

            loop.push_back({h_val, m_par, m_perp, current_theta});
        }

        return loop;
    }

    // Обчислення координат критичної астроїди
    struct AstroidPoint { double hx; double hz; };
    std::vector<AstroidPoint> calculate_astroid(int points = 100) const {
        std::vector<AstroidPoint> astroid;
        astroid.reserve(points);

        for (int i = 0; i < points; ++i) {
            double t = 2.0 * M_PI * i / points;
            double hx = std::pow(std::sin(t), 3);
            double hz = std::pow(std::cos(t), 3);
            astroid.push_back({hx, hz});
        }
        return astroid;
    }
};

int main() {
    MaterialProperties cobalt;
    AnisotropySimulator sim(cobalt);

    std::cout << "========================================================" << std::endl;
    std::cout << "  СИМУЛЯЦІЯ МАГНІТНОЇ АНІЗОТРОПІЇ СТОНЕРА - ВОЛЬФАРТА  " << std::endl;
    std::cout << "========================================================" << std::endl;
    std::cout << "Матеріал: " << cobalt.name << std::endl;
    std::cout << "Константа K1: " << cobalt.K1 << " Дж/м³" << std::endl;
    std::cout << "Поле анізотропії HA: " << sim.anisotropy_field() / 1e3 << " кА/м" << std::endl;
    std::cout << "--------------------------------------------------------" << std::endl;

    // Симуляція для трьох стандартних кутів: 0°, 45°, 90°
    std::vector<double> angles = {0.0, 45.0, 90.0};

    for (double angle : angles) {
        auto loop = sim.run_hysteresis_loop(angle, 100);
        std::cout << "\n>>> Кут прикладання поля θ_H = " << angle << "° <<<" << std::endl;
        std::cout << "  h (H/HA)  |  m_parallel  |  m_perp  |  θ (град)" << std::endl;
        std::cout << "------------------------------------------------" << std::endl;

        for (size_t i = 0; i < loop.size(); i += 25) {
            std::cout << std::fixed << std::setprecision(3)
                      << std::setw(9) << loop[i].h_applied << "  |  "
                      << std::setw(10) << loop[i].m_parallel << "  |  "
                      << std::setw(6) << loop[i].m_perpendicular << "  |  "
                      << std::setw(8) << loop[i].theta * 180.0 / M_PI << std::endl;
        }
    }

    return 0;
}
