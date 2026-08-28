#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <stdexcept>

struct SimParams {
    double W = 0.02;        // Товщина напівпровідника, см
    double D = 35.0;        // Коефіцієнт дифузії, см²/с
    double tau = 10e-6;     // Час життя носіїв, с
    double G0 = 1e20;       // Початкова швидкість генерації, см⁻³с⁻¹
    double alpha = 500.0;   // Коефіцієнт поглинання, см⁻¹
    double dn_surf = 1e14;  // Поверхнева концентрація, см⁻³

    [[nodiscard]] double diffusion_length() const noexcept {
        return std::sqrt(D * tau);
    }
};

struct SimulationResult {
    std::vector<double> x;
    std::vector<double> dn;
    double total_charge = 0.0;
};

class DiffusionSolver {
public:
    static SimulationResult solve(const SimParams& p, std::size_t N) {
        if (N < 3) {
            throw std::invalid_argument("Кількість вузлів N повинна бути принаймні 3");
        }

        SimulationResult res;
        res.x.resize(N);
        res.dn.resize(N);

        const double h = p.W / static_cast<double>(N - 1);
        const double L = p.diffusion_length();
        const double gamma = (h * h) / (L * L);
        const double h2_D = (h * h) / p.D;

        std::vector<double> a(N), b(N), c(N), d(N);
        std::vector<double> c_star(N), d_star(N);

        for (std::size_t i = 0; i < N; ++i) {
            res.x[i] = static_cast<double>(i) * h;
            const double G_i = p.G0 * std::exp(-p.alpha * res.x[i]);

            if (i == 0) {
                b[i] = 1.0;
                c[i] = 0.0;
                d[i] = p.dn_surf;
            } else if (i == N - 1) {
                a[i] = 0.0;
                b[i] = 1.0;
                d[i] = 0.0;
            } else {
                a[i] = 1.0;
                b[i] = -(2.0 + gamma);
                c[i] = 1.0;
                d[i] = -h2_D * G_i;
            }
        }

        // Прямий хід прогонки
        c_star[0] = c[0] / b[0];
        d_star[0] = d[0] / b[0];
        for (std::size_t i = 1; i < N; ++i) {
            const double m = b[i] - a[i] * c_star[i - 1];
            c_star[i] = c[i] / m;
            d_star[i] = (d[i] - a[i] * d_star[i - 1]) / m;
        }

        // Зворотний хід прогонки
        res.dn[N - 1] = d_star[N - 1];
        for (std::size_t i = N - 2; ; --i) {
            res.dn[i] = d_star[i] - c_star[i] * res.dn[i + 1];
            if (i == 0) break;
        }

        // Чисельне інтегрування накопиченого заряду методом трапецій
        double sum = 0.0;
        for (std::size_t i = 0; i < N - 1; ++i) {
            sum += 0.5 * (res.dn[i] + res.dn[i + 1]) * h;
        }
        constexpr double q_elem = 1.602176634e-19;
        res.total_charge = q_elem * sum;

        return res;
    }
};

int main() {
    SimParams params;
    const std::size_t N = 101;

    try {
        auto result = DiffusionSolver::solve(params, N);

        std::cout << "Дифузійна довжина L = " << std::fixed << std::setprecision(2) 
                  << params.diffusion_length() * 1e4 << " мкм\n";
        std::cout << "Накопичений заряд Q = " << std::scientific << std::setprecision(3) 
                  << result.total_charge << " Кл/см²\n\n";

        std::cout << "Вузол\tx (мкм)\t\tΔn (см⁻³)\n";
        for (std::size_t i = 0; i < N; i += 20) {
            std::cout << i << "\t" << std::fixed << std::setprecision(2) << result.x[i] * 1e4
                      << "\t\t" << std::scientific << std::setprecision(3) << result.dn[i] << "\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
