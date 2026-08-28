#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <memory>
#include <stdexcept>

namespace spin_caloritronics {

// Фізичні фундаментальні константи
constexpr double electron_charge = 1.602176634e-19; // Кл
constexpr double reduced_planck  = 1.054571817e-34;  // Дж·с
constexpr double boltzmann_const  = 1.380649e-23;    // Дж/К

// Структура параметрів гетероструктури
struct DeviceParameters {
    std::size_t num_points{500};
    double layer_thickness{1.0e-6};  // 1 мкм YIG
    double lambda_m{100.0e-9};        // 100 нм довжина дифузії
    double sigma_m{1.0e3};            // 1000 Ом^-1·м^-1
    double g_mix{1.0e18};             // 1e18 м^-2 провідність змішування
    double theta_sh{0.08};            // 8% спіновий кут Холла Pt
    double rho_pt{2.0e-7};            // 200 нОм·м
    double pt_thickness{10.0e-9};     // 10 нм товщина Pt
    double sample_width{5.0e-3};      // 5 мм ширина зразка
    double temp_cold{300.0};          // 300 K
    double temp_hot{310.0};           // 310 K
};

// Клас розрахунку профілю магнонної дифузії (RAII та безпечна робота з контейнерами)
class MagnonDiffusionSolver {
public:
    explicit MagnonDiffusionSolver(DeviceParameters params)
        : params_(std::move(params)),
          z_mesh_(params_.num_points, 0.0),
          mu_m_(params_.num_points, 0.0),
          temp_profile_(params_.num_points, 0.0) {
        initialize_mesh();
    }

    void solve(std::size_t max_iterations = 100000, double tolerance = 1.0e-12) {
        const std::size_t n = params_.num_points;
        const double dz = params_.layer_thickness / static_cast<double>(n - 1);
        const double dz_sq = dz * dz;
        const double inv_lambda_sq = 1.0 / (params_.lambda_m * params_.lambda_m);
        const double denom = 2.0 + dz_sq * inv_lambda_sq;

        std::vector<double> next_mu(n, 0.0);

        for (std::size_t iter = 0; iter < max_iterations; ++iter) {
            double max_change = 0.0;

            // Внутрішній сітковий релаксаційний крок
            for (std::size_t i = 1; i < n - 1; ++i) {
                next_mu[i] = (mu_m_[i - 1] + mu_m_[i + 1]) / denom;
                max_change = std::max(max_change, std::abs(next_mu[i] - mu_m_[i]));
            }

            // Межова умова зазору Неймана z = 0
            next_mu[0] = next_mu[1];

            // Межова умова спінового випромінювання z = L
            const double alpha = (params_.g_mix * electron_charge) / 
                                 (std::numbers::pi * params_.sigma_m);
            next_mu[n - 1] = next_mu[n - 2] / (1.0 + dz * alpha);

            mu_m_ = next_mu;

            if (max_change < tolerance && iter > 100) {
                break;
            }
        }

        compute_physical_outputs();
    }

    [[nodiscard]] double ishe_voltage() const noexcept { return ishe_voltage_; }
    [[nodiscard]] double spin_current() const noexcept { return spin_current_; }
    [[nodiscard]] double boundary_accumulation() const noexcept { return mu_m_.back(); }
    [[nodiscard]] const std::vector<double>& z_mesh() const noexcept { return z_mesh_; }
    [[nodiscard]] const std::vector<double>& mu_m() const noexcept { return mu_m_; }

private:
    void initialize_mesh() {
        const std::size_t n = params_.num_points;
        const double dz = params_.layer_thickness / static_cast<double>(n - 1);
        for (std::size_t i = 0; i < n; ++i) {
            z_mesh_[i] = static_cast<double>(i) * dz;
            temp_profile_[i] = params_.temp_cold + 
                (params_.temp_hot - params_.temp_cold) * (z_mesh_[i] / params_.layer_thickness);
        }
    }

    void compute_physical_outputs() {
        const double boundary_mu = mu_m_.back();
        spin_current_ = (params_.g_mix / (2.0 * std::numbers::pi)) * boundary_mu;
        
        ishe_voltage_ = params_.theta_sh * (params_.rho_pt / params_.pt_thickness) *
                        params_.sample_width * spin_current_ * (electron_charge / reduced_planck);
    }

    DeviceParameters params_;
    std::vector<double> z_mesh_;
    std::vector<double> mu_m_;
    std::vector<double> temp_profile_;
    double ishe_voltage_{0.0};
    double spin_current_{0.0};
};

} // namespace spin_caloritronics

int main() {
    using namespace spin_caloritronics;

    try {
        DeviceParameters params;
        MagnonDiffusionSolver solver(params);
        solver.solve();

        std::cout << std::scientific << std::setprecision(4);
        std::cout << "=== Спінова калоритроніка: Чисельний розрахунок YIG/Pt (C++) ===\n";
        std::cout << "Магнонний потенціал на межі (z=L): " << solver.boundary_accumulation() << " Дж\n";
        std::cout << "Інжектований спіновий струм J_s:     " << solver.spin_current() << " Дж/м^2\n";
        std::cout << "Поперечна напруга ISHE V_ISHE:       " << solver.ishe_voltage() << " В ("
                  << std::fixed << std::setprecision(2) << solver.ishe_voltage() * 1.0e6 << " мкВ)\n";
    }
    catch (const std::exception& ex) {
        std::cerr << "Помилка під час виконання розрахунку: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
