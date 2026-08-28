#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <stdexcept>
#include <span>
#include <numeric>

// Фундаментальні фізичні константи
constexpr double Q_E = 1.60217663e-19;     // Заряд електрона (Кл)
constexpr double KB = 1.380649e-23;        // Константа Больцмана (Дж/К)
constexpr double EPS0 = 8.85418781e-12;    // Діелектрична стала вакууму (Ф/м)

struct Material {
    double eg;       // Ширина забороненої зони (еВ)
    double chi;      // Спорідненість до електрона (еВ)
    double epsr;     // Відносна діелектрична проникність
    double nc;       // Щільність станів (м^-3)
    double nd;       // Концентрація донорів (м^-3)
};

class HeterojunctionSolver {
public:
    HeterojunctionSolver(Material mat1, Material mat2, double length_nm, std::size_t num_nodes)
        : mat1_(mat1), mat2_(mat2), num_nodes_(num_nodes),
          dz_((length_nm * 1e-9) / (num_nodes - 1)), k_int_(num_nodes / 2),
          phi_(num_nodes, 0.0), ec_(num_nodes, 0.0), n_(num_nodes, 0.0),
          eps_(num_nodes, 0.0), nd_(num_nodes, 0.0)
    {
        if (num_nodes < 20) {
            throw std::invalid_argument("Сітка повинна містити щонайменше 20 вузлів для точної дискретизації.");
        }
        for (std::size_t i = 0; i < num_nodes_; ++i) {
            const auto& m = (i < k_int_) ? mat1_ : mat2_;
            eps_[i] = m.epsr * EPS0;
            nd_[i] = m.nd;
            ec_[i] = -m.chi;
        }
    }

    void solve(double temp_k = 300.0, std::size_t max_iter = 4000, double tol = 1e-6) {
        const double vt = (KB * temp_k) / Q_E;
        constexpr double alpha = 0.08; // Коефіцієнт релаксації

        for (std::size_t iter = 0; iter < max_iter; ++iter) {
            double max_change = 0.0;

            // Оновлення концентрації електронів n[i]
            for (std::size_t i = 0; i < num_nodes_; ++i) {
                const auto& m = (i < k_int_) ? mat1_ : mat2_;
                const double ec0 = -m.chi;
                ec_[i] = ec0 - phi_[i];
                n_[i] = m.nc * std::exp(-ec_[i] / vt);
            }

            // Перерахунок потенціалу методом Гаусса — Зайделя
            for (std::size_t i = 1; i < num_nodes_ - 1; ++i) {
                const double eps_p = 0.5 * (eps_[i] + eps_[i + 1]);
                const double eps_m = 0.5 * (eps_[i] + eps_[i - 1]);
                const double rho = Q_E * (nd_[i] - n_[i]);

                const double phi_new = (eps_p * phi_[i + 1] + eps_m * phi_[i - 1] + rho * dz_ * dz_) / (eps_p + eps_m);
                const double diff = std::abs(phi_new - phi_[i]);
                if (diff > max_change) max_change = diff;

                phi_[i] = (1.0 - alpha) * phi_[i] + alpha * phi_new;
            }

            if (max_change < tol) {
                std::cout << "Ітераційний процес успішно збігся за " << iter << " ітерацій.\n";
                return;
            }
        }
        throw std::runtime_error("Перевищено максимальну кількість ітерацій Пуассона без досягнення збіжності.");
    }

    [[nodiscard]] double compute_2deg_sheet_density() const noexcept {
        double ns = 0.0;
        for (std::size_t i = k_int_; i < num_nodes_; ++i) {
            ns += n_[i] * dz_;
        }
        return ns * 1e-4; // Переведення в см^-2
    }

    [[nodiscard]] std::span<const double> get_ec() const noexcept { return ec_; }
    [[nodiscard]] std::span<const double> get_phi() const noexcept { return phi_; }
    [[nodiscard]] std::span<const double> get_n() const noexcept { return n_; }
    [[nodiscard]] double get_dz() const noexcept { return dz_; }
    [[nodiscard]] std::size_t get_num_nodes() const noexcept { return num_nodes_; }

private:
    Material mat1_;
    Material mat2_;
    std::size_t num_nodes_;
    double dz_;
    std::size_t k_int_;
    std::vector<double> phi_;
    std::vector<double> ec_;
    std::vector<double> n_;
    std::vector<double> eps_;
    std::vector<double> nd_;
};

int main() {
    try {
        Material algaas{ .eg = 1.80, .chi = 3.74, .epsr = 12.2, .nc = 1.5e23, .nd = 1e24 };
        Material gaas  { .eg = 1.42, .chi = 4.07, .epsr = 13.1, .nc = 4.7e23, .nd = 1e20 };

        HeterojunctionSolver solver(algaas, gaas, 100.0, 200);
        solver.solve(300.0);

        std::cout << "\n=======================================================\n";
        std::cout << "  Обчислення профілю 2DEG N-AlGaAs / i-GaAs (C++)\n";
        std::cout << "=======================================================\n";
        std::cout << std::scientific << std::setprecision(3);
        std::cout << "Густина 2DEG каналу n_s = " << solver.compute_2deg_sheet_density() << " см^-2\n\n";

        std::cout << std::fixed << std::setprecision(2);
        std::cout << "z (нм)\t\tEc (еВ)\t\tПотенціал (В)\tn (см^-3)\n";
        std::cout << "-------------------------------------------------------\n";

        auto ec = solver.get_ec();
        auto phi = solver.get_phi();
        auto n = solver.get_n();

        for (std::size_t i = 0; i < solver.get_num_nodes(); i += 15) {
            double z_nm = i * solver.get_dz() * 1e9;
            std::cout << z_nm << " нм\t\t" << ec[i] << " еВ\t\t" << phi[i] << " В\t\t"
                      << std::scientific << std::setprecision(2) << n[i] * 1e-6 << " см^-3\n"
                      << std::fixed << std::setprecision(2);
        }
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка розрахунку: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
