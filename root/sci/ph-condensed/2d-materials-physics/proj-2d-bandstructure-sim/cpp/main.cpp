#include <iostream>
#include <vector>
#include <cmath>
#include <complex>
#include <iomanip>
#include <utility>

struct BandState {
    double kx;
    double ky;
    double energy_valence;
    double energy_conduction;
};

class GrapheneTightBindingCalculator {
private:
    double a_cc; // Довжина ковалентного зв'язку C-C (нм)
    double t;    // Інтеграл перескоку найближчих сусідів (еВ)

public:
    explicit GrapheneTightBindingCalculator(double bond_len = 0.142, double hopping = 2.7)
        : a_cc(bond_len), t(hopping) {}

    std::pair<double, double> compute_band_energies(double kx, double ky) const {
        using namespace std::complex_literals;

        std::complex<double> phase1(0.0, ky * a_cc);
        std::complex<double> phase2(0.0, -ky * a_cc / 2.0);
        double cos_factor = std::cos(kx * a_cc * std::sqrt(3.0) / 2.0);

        // Комплексна функція перескоку f(k)
        std::complex<double> f_k = -t * (std::exp(phase1) + 2.0 * std::exp(phase2) * cos_factor);
        double energy_magnitude = std::abs(f_k);

        return {-energy_magnitude, +energy_magnitude};
    }

    std::vector<BandState> calculate_brillouin_path(std::size_t steps_per_segment) const {
        const double pi = std::acos(-1.0);

        const std::pair<double, double> gamma{0.0, 0.0};
        const std::pair<double, double> k_point{2.0 * pi / (3.0 * a_cc * std::sqrt(3.0)), 2.0 * pi / (3.0 * a_cc)};
        const std::pair<double, double> m_point{0.0, 2.0 * pi / (3.0 * a_cc)};

        std::vector<BandState> path_data;
        path_data.reserve(steps_per_segment * 3);

        auto append_segment = [this, steps_per_segment, &path_data](auto p_start, auto p_end) {
            for (std::size_t i = 0; i < steps_per_segment; ++i) {
                double alpha = static_cast<double>(i) / static_cast<double>(steps_per_segment);
                double kx = p_start.first + alpha * (p_end.first - p_start.first);
                double ky = p_start.second + alpha * (p_end.second - p_start.second);

                auto [e_v, e_c] = this->compute_band_energies(kx, ky);
                path_data.push_back({kx, ky, e_v, e_c});
            }
        };

        append_segment(gamma, k_point);
        append_segment(k_point, m_point);
        append_segment(m_point, gamma);

        return path_data;
    }
};

int main() {
    GrapheneTightBindingCalculator calculator(0.142, 2.7);
    const std::size_t resolution = 100;
    auto band_structure = calculator.calculate_brillouin_path(resolution);

    std::cout << std::fixed << std::setprecision(5);
    std::cout << "=========================================================\n";
    std::cout << "  РЕЗУЛЬТАТИ ОБЧИСЛЕННЯ ЗОННОЇ СТРУКТУРИ ГРАФЕНА (C++17) \n";
    std::cout << "=========================================================\n";
    std::cout << "Загальна кількість точок розрахунку: " << band_structure.size() << "\n\n";

    std::cout << "1. Точка Gamma (k = 0):\n";
    std::cout << "   E_val = " << band_structure[0].energy_valence 
              << " eV, E_con = " << band_structure[0].energy_conduction << " eV\n\n";

    std::cout << "2. Точка K (Конус Дірака):\n";
    std::cout << "   E_val = " << band_structure[resolution].energy_valence 
              << " eV, E_con = " << band_structure[resolution].energy_conduction << " eV\n\n";

    std::cout << "3. Точка M:\n";
    std::cout << "   E_val = " << band_structure[2 * resolution].energy_valence 
              << " eV, E_con = " << band_structure[2 * resolution].energy_conduction << " eV\n";

    return 0;
}
