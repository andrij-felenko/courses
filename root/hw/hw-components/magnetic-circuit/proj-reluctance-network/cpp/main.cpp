#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <string_view>
#include <algorithm>

namespace mag {

constexpr double Mu0 = 1.2566370614359173e-6;

enum class Material {
    LinearAir,
    FerriteN87
};

struct Branch {
    std::string_view name;
    int node_from{0};
    int node_to{0};
    double length{0.0};     // Довжина магнітної лінії, м
    double area{0.0};       // Площа перерізу, м^2
    double mmf{0.0};        // Ампер-витки N*I, А-вит
    Material mat{Material::FerriteN87};
    double mu_r0{2200.0};
    double b_sat{0.39};

    // Стан після розрахунку
    double mu_r{1.0};
    double permeance{0.0};
    double flux{0.0};
    double b_field{0.0};
    double h_field{0.0};
};

class ReluctanceSolver {
public:
    ReluctanceSolver(int nodes, int ground, std::vector<Branch> branches)
        : num_nodes_(nodes), ground_node_(ground), branches_(std::move(branches)) {}

    bool solve(double tolerance = 1e-6, int max_iterations = 200, double alpha = 0.35) {
        for (auto& br : branches_) {
            br.mu_r = (br.mat == Material::LinearAir) ? 1.0 : br.mu_r0;
        }

        const int n_eq = num_nodes_ - 1;
        std::vector<double> potentials(num_nodes_, 0.0);

        for (int iter = 0; iter < max_iterations; ++iter) {
            for (auto& br : branches_) {
                br.permeance = Mu0 * br.mu_r * br.area / br.length;
            }

            std::vector<std::vector<double>> G(n_eq, std::vector<double>(n_eq, 0.0));
            std::vector<double> RHS(n_eq, 0.0);

            for (const auto& br : branches_) {
                int u = br.node_from;
                int v = br.node_to;
                double p = br.permeance;
                double src = p * br.mmf;

                if (u != ground_node_) {
                    G[u][u] += p;
                    RHS[u] -= src;
                    if (v != ground_node_) G[u][v] -= p;
                }
                if (v != ground_node_) {
                    G[v][v] += p;
                    RHS[v] += src;
                    if (u != ground_node_) G[v][u] -= p;
                }
            }

            std::vector<double> V_sol(n_eq, 0.0);
            if (!solveGaussian(G, RHS, V_sol)) {
                std::cerr << "Помилка: вироджена матриця магнітної сітки!\n";
                return false;
            }

            for (int i = 0; i < n_eq; ++i) potentials[i] = V_sol[i];
            potentials[ground_node_] = 0.0;

            double max_rel_err = 0.0;
            for (auto& br : branches_) {
                double v_from = potentials[br.node_from];
                double v_to = potentials[br.node_to];
                double drop = v_from - v_to + br.mmf;
                br.h_field = std::abs(drop) / br.length;

                if (br.mat == Material::FerriteN87) {
                    double target_mur = calcBrauerMur(br.h_field, br.mu_r0, br.b_sat);
                    double err = std::abs(target_mur - br.mu_r) / br.mu_r;
                    max_rel_err = std::max(max_rel_err, err);
                    br.mu_r = (1.0 - alpha) * br.mu_r + alpha * target_mur;
                }
            }

            if (max_rel_err < tolerance) {
                for (auto& br : branches_) {
                    double v_from = potentials[br.node_from];
                    double v_to = potentials[br.node_to];
                    br.flux = br.permeance * (v_from - v_to + br.mmf);
                    br.b_field = std::abs(br.flux) / br.area;
                }
                return true;
            }
        }
        return false;
    }

    const std::vector<Branch>& branches() const noexcept { return branches_; }

private:
    static double calcBrauerMur(double h, double mu_r0, double b_sat) noexcept {
        if (h < 1e-9) return mu_r0;
        const double h_c = b_sat / (Mu0 * (mu_r0 - 1.0));
        return 1.0 + (b_sat / Mu0) / (h + h_c);
    }

    static bool solveGaussian(std::vector<std::vector<double>>& A, std::vector<double>& b, std::vector<double>& x) {
        const int n = static_cast<int>(b.size());
        for (int i = 0; i < n; ++i) {
            int max_row = i;
            for (int k = i + 1; k < n; ++k) {
                if (std::abs(A[k][i]) > std::abs(A[max_row][i])) max_row = k;
            }
            std::swap(A[i], A[max_row]);
            std::swap(b[i], b[max_row]);

            if (std::abs(A[i][i]) < 1e-20) return false;

            for (int k = i + 1; k < n; ++k) {
                double factor = A[k][i] / A[i][i];
                b[k] -= factor * b[i];
                for (int j = i; j < n; j++) A[k][j] -= factor * A[i][j];
            }
        }

        for (int i = n - 1; i >= 0; --i) {
            double sum = 0.0;
            for (int j = i + 1; j < n; ++j) sum += A[i][j] * x[j];
            x[i] = (b[i] - sum) / A[i][i];
        }
        return true;
    }

    int num_nodes_;
    int ground_node_;
    std::vector<Branch> branches_;
};

} // namespace mag

int main() {
    using namespace mag;

    std::vector<Branch> branches = {
        {"Центральний керн (ферит)", 0, 1, 0.035, 1.78e-4, 180.0, Material::FerriteN87, 2200.0, 0.39},
        {"Повітряний зазор керна",   0, 1, 0.0008, 1.78e-4, 0.0,   Material::LinearAir,  1.0,    0.0},
        {"Ліва гілка (бічний керн)", 0, 1, 0.065, 0.89e-4, 0.0,   Material::FerriteN87, 2200.0, 0.39},
        {"Права гілка (бічний керн)",0, 1, 0.065, 0.89e-4, 0.0,   Material::FerriteN87, 2200.0, 0.39}
    };

    ReluctanceSolver solver(2, 1, std::move(branches));

    std::cout << "=== Чисельний розрахунок розгалуженого магнітного кола (C++) ===\n";
    if (solver.solve(1e-6, 200, 0.35)) {
        std::cout << "Збіжність досягнута успішно.\n\n";
        std::cout << std::fixed << std::setprecision(3);
        for (const auto& br : solver.branches()) {
            std::cout << std::left << std::setw(28) << br.name << ": "
                      << "Потік = " << std::setw(7) << br.flux * 1e6 << " мкВб | "
                      << "B = " << std::setw(5) << br.b_field << " Тл | "
                      << "H = " << std::setw(6) << std::setprecision(1) << br.h_field << " А/м | "
                      << "mu_r = " << std::setw(6) << br.mu_r << "\n";
            std::cout << std::setprecision(3);
        }

        const double turns = 40.0;
        const double current = 4.5;
        const double flux_center = std::abs(solver.branches()[0].flux);
        const double inductance = (turns * flux_center) / current;

        std::cout << "\nРезультуюча індуктивність L: " << std::setprecision(2) << inductance * 1e6 << " мкГн\n";
        std::cout << "Запас до насичення центрального керна: " << std::setprecision(1)
                  << (1.0 - solver.branches()[0].b_field / 0.39) * 100.0 << "%\n";
    } else {
        std::cerr << "Розрахунок не зійшовся за максимальну кількість ітерацій.\n";
    }
    return 0;
}
