/* 
 * 1D Transient Thermal Diffusion & Laser Flash Solver in C++20
 * Ідіоматична реалізація: RAII, std::vector, std::span, std::expected.
 */

#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <expected>
#include <iomanip>

struct SimulationConfig {
    std::size_t N{101};          // Кількість вузлів
    double L{0.002};             // Товщина зразка, м
    double a_true{1.17e-4};      // Еталонне значення a, м²/с
    double dt{1.0e-5};           // Крок за часом, с
    double t_max{0.02};          // Повний час моделювання, с
};

struct ThermalAnalysisResult {
    double a_extracted{0.0};
    double t_half{0.0};
    double max_temp_rear{0.0};
    double error_percent{0.0};
};

enum class SolverError {
    InvalidParameters,
    AllocationFailure,
    ConvergenceError
};

class CrankNicolsonSolver {
public:
    explicit CrankNicolsonSolver(const SimulationConfig& config)
        : cfg_{config}, dx_{config.L / static_cast<double>(config.N - 1)} 
    {
        T_.resize(cfg_.N, 0.0);
        T_new_.resize(cfg_.N, 0.0);
        a_diag_.resize(cfg_.N, 0.0);
        b_diag_.resize(cfg_.N, 0.0);
        c_diag_.resize(cfg_.N, 0.0);
        d_vec_.resize(cfg_.N, 0.0);
        P_.resize(cfg_.N, 0.0);
        Q_.resize(cfg_.N, 0.0);
    }

    std::expected<ThermalAnalysisResult, SolverError> execute() {
        if (cfg_.N < 3 || cfg_.L <= 0.0 || cfg_.a_true <= 0.0) {
            return std::unexpected(SolverError::InvalidParameters);
        }

        const double r = cfg_.a_true * cfg_.dt / (2.0 * dx_ * dx_);
        
        // Імпульсний нагрів передньої грані (i = 0)
        constexpr double Q_laser = 100.0;
        T_[0] += Q_laser / dx_;

        const double T_initial_rear = T_.back();
        double max_rear_temp = 0.0;
        
        const auto total_steps = static_cast<std::size_t>(cfg_.t_max / cfg_.dt);
        std::vector<double> rear_history;
        std::vector<double> time_history;
        rear_history.reserve(total_steps);
        time_history.reserve(total_steps);

        for (std::size_t step = 0; step < total_steps; ++step) {
            const double current_time = static_cast<double>(step) * cfg_.dt;
            time_history.push_back(current_time);
            rear_history.push_back(T_.back());

            if (T_.back() > max_rear_temp) {
                max_rear_temp = T_.back();
            }

            // Збірка СЛАР для внутрішніх вузлів
            for (std::size_t i = 1; i < cfg_.N - 1; ++i) {
                a_diag_[i] = -r;
                b_diag_[i] = 1.0 + 2.0 * r;
                c_diag_[i] = -r;
                d_vec_[i] = r * T_[i - 1] + (1.0 - 2.0 * r) * T_[i] + r * T_[i + 1];
            }

            // Граничні умови Неймана (адіабатичні межі)
            a_diag_[0] = 0.0;
            b_diag_[0] = 1.0 + 2.0 * r;
            c_diag_[0] = -2.0 * r;
            d_vec_[0] = (1.0 - 2.0 * r) * T_[0] + 2.0 * r * T_[1];

            a_diag_[cfg_.N - 1] = -2.0 * r;
            b_diag_[cfg_.N - 1] = 1.0 + 2.0 * r;
            c_diag_[cfg_.N - 1] = 0.0;
            d_vec_[cfg_.N - 1] = 2.0 * r * T_[cfg_.N - 2] + (1.0 - 2.0 * r) * T_.back();

            // Розв'язання тридіагональної системи методому Томаса
            solve_thomas();
            T_ = T_new_;
        }

        // Автоекстракція t_{1/2}
        const double target_half_temp = T_initial_rear + 0.5 * (max_rear_temp - T_initial_rear);
        double t_half = -1.0;

        for (std::size_t step = 0; step < total_steps; ++step) {
            if (rear_history[step] >= target_half_temp) {
                if (step > 0) {
                    const double t0 = time_history[step - 1];
                    const double t1 = time_history[step];
                    const double v0 = rear_history[step - 1];
                    const double v1 = rear_history[step];
                    t_half = t0 + (target_half_temp - v0) * (t1 - t0) / (v1 - v0);
                } else {
                    t_half = time_history[step];
                }
                break;
            }
        }

        if (t_half <= 0.0) {
            return std::unexpected(SolverError::ConvergenceError);
        }

        const double a_extracted = 0.1388 * cfg_.L * cfg_.L / t_half;
        const double err_pct = std::abs(a_extracted - cfg_.a_true) / cfg_.a_true * 100.0;

        return ThermalAnalysisResult{
            .a_extracted = a_extracted,
            .t_half = t_half,
            .max_temp_rear = max_rear_temp,
            .error_percent = err_pct
        };
    }

private:
    void solve_thomas() {
        const std::size_t N = cfg_.N;
        P_[0] = -c_diag_[0] / b_diag_[0];
        Q_[0] = d_vec_[0] / b_diag_[0];

        for (std::size_t i = 1; i < N; ++i) {
            const double denom = b_diag_[i] + a_diag_[i] * P_[i - 1];
            if (i < N - 1) {
                P_[i] = -c_diag_[i] / denom;
            }
            Q_[i] = (d_vec_[i] - a_diag_[i] * Q_[i - 1]) / denom;
        }

        T_new_[N - 1] = Q_[N - 1];
        for (std::size_t i = N - 2; i < N; --i) { // Використання підповзання беззнакового ітератора
            T_new_[i] = P_[i] * T_new_[i + 1] + Q_[i];
            if (i == 0) break;
        }
    }

    SimulationConfig cfg_;
    double dx_;
    std::vector<double> T_;
    std::vector<double> T_new_;
    std::vector<double> a_diag_;
    std::vector<double> b_diag_;
    std::vector<double> c_diag_;
    std::vector<double> d_vec_;
    std::vector<double> P_;
    std::vector<double> Q_;
};

int main() {
    std::cout << "=== Чисельне моделювання LFA (C++20) ===\n";

    SimulationConfig config{
        .N = 101,
        .L = 0.002,
        .a_true = 1.17e-4, // Мідь
        .dt = 1.0e-5,
        .t_max = 0.02
    };

    CrankNicolsonSolver solver(config);
    auto result = solver.execute();

    if (result) {
        std::cout << std::scientific << std::setprecision(6);
        std::cout << "Задана температуропровідність a: " << config.a_true << " м²/с\n";
        std::cout << "Екстрагована значення з LFA:    " << result->a_extracted << " м²/с\n";
        std::cout << "Час напівпідйому t₁/₂:          " << result->t_half * 1000.0 << " мс\n";
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "Відносна похибка розрахунку:   " << result->error_percent << " %\n";
    } else {
        std::cerr << "Помилка обчислення солвера!\n";
    }

    return 0;
}
