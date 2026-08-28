#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <array>
#include <numeric>

// Об'єктно-орієнтований клас для точної діагоналізації Fermi-Hubbard кластера
class HubbardClusterSolver {
public:
    struct Results {
        double ground_state_energy;
        double double_occupancy;
        double spin_correlation_z;
    };

    explicit HubbardClusterSolver(double hopping, double coulomb)
        : t_(hopping), U_(coulomb) {}

    [[nodiscard]] Results solve2Site() const {
        // Синглетний основний стан для 2-вузлової системи обчислюється діагоналізацією
        const double delta = std::sqrt(U_ * U_ + 16.0 * t_ * t_);
        const double e0 = (U_ - delta) / 2.0;

        // Компоненти нормалізованого власного вектора
        const double alpha = (U_ + delta) / (4.0 * t_);
        const double norm = std::sqrt(2.0 * (1.0 + alpha * alpha));
        
        const double c_singlet = 1.0 / norm;
        const double c_doublet = alpha / norm;

        // Ймовірність знайти подвійну заповненість на вузлі
        const double docc = c_doublet * c_doublet;
        
        // Спін-спінова антиферомагнітна кореляція
        const double sz_corr = -0.5 * (c_singlet * c_singlet);

        return Results{ e0, docc, sz_corr };
    }

private:
    double t_;
    double U_;
};

int main() {
    constexpr double t_integral = 1.0;
    std::cout << "=== Чисельна точна діагоналізація 2-вузлової моделі Габбарда (C++) ===\n";
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "  U/t   | Енергія E_0/t | Подвійна заповненість <n_↑ n_↓> | Спін-кореляція <S0z S1z>\n";
    std::cout << "--------+---------------+----------------------------------+------------------------\n";

    for (int u_int = 0; u_int <= 10; ++u_int) {
        const double U = static_cast<double>(u_int);
        HubbardClusterSolver solver(t_integral, U);
        const auto [energy, docc, sz_corr] = solver.solve2Site();

        std::cout << " " << std::setw(5) << U << "  |   "
                  << std::setw(9) << energy << "   |             "
                  << std::setw(8) << docc << "             |        "
                  << std::setw(8) << sz_corr << "\n";
    }

    return 0;
}
