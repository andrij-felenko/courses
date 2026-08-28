#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <stdexcept>

// Електрична стала ε0 (Ф/м)
constexpr double EPSILON_0 = 8.854187817e-12;

enum class NodeKind {
    Free,       // Вільний вузол діелектрика або внутрішнього провідника
    Conductor,  // Внутрішній вузол провідника
    Boundary,   // Вузол бічної поверхні провідника
    Source,     // Вхідний електрод джерела (V = V_in)
    Ground      // Вихідний заземлений електрод (V = 0)
};

struct SimulationConfig {
    std::size_t nx{80};
    std::size_t ny{80};
    double grid_step{1e-3};      // Крок сітки (1 мм)
    double v_in{10.0};           // Вхідна напруга (10 В)
    double omega{1.85};          // Параметр верхньої релаксації (SOR)
    double tolerance{1e-6};     // Поріг збіжності
    std::size_t max_iterations{5000};
};

class SurfaceChargeSolver {
public:
    explicit SurfaceChargeSolver(SimulationConfig cfg)
        : config_(cfg),
          v_(cfg.nx, std::vector<double>(cfg.ny, 0.0)),
          kind_(cfg.nx, std::vector<NodeKind>(cfg.ny, NodeKind::Free)) {
        setup_geometry();
    }

    void solve() {
        std::size_t iter = 0;
        double max_diff = 0.0;
        do {
            max_diff = 0.0;
            for (std::size_t i = 1; i < config_.nx - 1; ++i) {
                for (std::size_t j = 1; j < config_.ny - 1; ++j) {
                    if (kind_[i][j] == NodeKind::Source || kind_[i][j] == NodeKind::Ground) {
                        continue;
                    }
                    const double old_val = v_[i][j];
                    const double target = 0.25 * (v_[i + 1][j] + v_[i - 1][j] + v_[i][j + 1] + v_[i][j - 1]);
                    const double updated = old_val + config_.omega * (target - old_val);
                    v_[i][j] = updated;
                    const double diff = std::abs(updated - old_val);
                    if (diff > max_diff) {
                        max_diff = diff;
                    }
                }
            }
            ++iter;
        } while (max_diff > config_.tolerance && iter < config_.max_iterations);

        std::cout << "Солівер збігся за " << iter << " ітерацій. Залишкова неузгодженість: " 
                  << max_diff << " В\n";
    }

    // Обчислення нормального поля та поверхневої густини заряду у вузлі (x, y)
    double compute_surface_charge(std::size_t i, std::size_t j, int normal_dx, int normal_dy) const {
        if (i == 0 || i >= config_.nx - 1 || j == 0 || j >= config_.ny - 1) {
            return 0.0;
        }
        // Одностороння похідна нормального поля у бік діелектрика
        const double v_surf = v_[i][j];
        const double v_ext = v_[i + normal_dx][j + normal_dy];
        const double e_normal = -(v_ext - v_surf) / config_.grid_step;
        return EPSILON_0 * e_normal;
    }

    void print_corner_charge_results() const {
        std::cout << "\n--- РЕЗУЛЬТАТИ ОБЧИСЛЕННЯ ПОВЕРХНЕВОГО ЗАРЯДУ НА ВИГИНІ ---\n";
        // Зовнішній кут провідника (x=20, y=20)
        const double sigma_outer = compute_surface_charge(20, 20, -1, -1);
        // Внутрішній кут провідника (x=40, y=40)
        const double sigma_inner = compute_surface_charge(40, 40, 1, 1);

        std::cout << std::scientific << std::setprecision(4);
        std::cout << "Густина заряду на зовнішньому куті (поперечний поворот): " 
                  << sigma_outer << " Кулон/м²\n";
        std::cout << "Густина заряду на внутрішньому куті: " 
                  << sigma_inner << " Кулон/м²\n";
    }

private:
    void setup_geometry() {
        // Формування L-подібного провідника у сітці 80х80
        // Вхідний канал (x від 20 до 40, y від 0 до 40)
        // Вихідний канал (x від 20 до 80, y від 20 до 40)
        for (std::size_t i = 20; i <= 40; ++i) {
            for (std::size_t j = 0; j <= 20; ++j) {
                kind_[i][j] = NodeKind::Conductor;
                v_[i][j] = config_.v_in * (1.0 - static_cast<double>(j) / 80.0);
            }
        }
        for (std::size_t i = 20; i <= 80; ++i) {
            for (std::size_t j = 20; j <= 40; ++j) {
                kind_[i][j] = NodeKind::Conductor;
                v_[i][j] = config_.v_in * (1.0 - static_cast<double>(i + j) / 120.0);
            }
        }
        // Початкові електроди
        for (std::size_t i = 20; i <= 40; ++i) {
            kind_[i][0] = NodeKind::Source;
            v_[i][0] = config_.v_in;
        }
        for (std::size_t j = 20; j <= 40; ++j) {
            kind_[80 - 1][j] = NodeKind::Ground;
            v_[80 - 1][j] = 0.0;
        }
    }

    SimulationConfig config_;
    std::vector<std::vector<double>> v_;
    std::vector<std::vector<NodeKind>> kind_;
};

int main() {
    try {
        SimulationConfig cfg;
        cfg.nx = 81;
        cfg.ny = 81;
        cfg.grid_step = 1e-3;
        cfg.v_in = 12.0;

        SurfaceChargeSolver solver(cfg);
        solver.solve();
        solver.print_corner_charge_results();

    } catch (const std::exception& e) {
        std::cerr << "Помилка обчислень: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
