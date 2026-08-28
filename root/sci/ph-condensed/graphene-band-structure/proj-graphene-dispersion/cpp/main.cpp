#include <iostream>
#include <vector>
#include <cmath>
#include <numeric>
#include <algorithm>

struct BandPoint {
    double kx;
    double ky;
    double e_val;
    double e_cond;
};

class GrapheneBandModel {
private:
    double t_;    // Інтеграл перескоку (еВ)
    double acc_;  // Відстань C-C (Ангстрем)

public:
    GrapheneBandModel(double t = 2.8, double acc = 1.42)
        : t_(t), acc_(acc) {}

    double calculate_factor(double kx, double ky) const {
        double kx_a = kx * acc_ * std::sqrt(3.0) / 2.0;
        double ky_a = ky * acc_ * 1.5;
        double cos_kx = std::cos(kx_a);
        double cos_ky = std::cos(ky_a);
        
        double f_sq = 1.0 + 4.0 * cos_kx * cos_ky + 4.0 * cos_kx * cos_kx;
        return (f_sq < 0.0) ? 0.0 : std::sqrt(f_sq);
    }

    BandPoint evaluate(double kx, double ky) const {
        double f = calculate_factor(kx, ky);
        return { kx, ky, -t_ * f, t_ * f };
    }

    std::vector<BandPoint> compute_high_symmetry_path(std::size_t points_per_segment = 200) const {
        std::vector<BandPoint> path;
        path.reserve(points_per_segment * 3);

        const double k_x_K = 4.0 * M_PI / (3.0 * std::sqrt(3.0) * acc_);
        const double k_y_K = 0.0;

        const double k_x_M = M_PI / (std::sqrt(3.0) * acc_);
        const double k_y_M = M_PI / (3.0 * acc_);

        // Сегмент 1: Gamma -> K
        for (std::size_t i = 0; i < points_per_segment; ++i) {
            double alpha = static_cast<double>(i) / points_per_segment;
            path.push_back(evaluate(alpha * k_x_K, alpha * k_y_K));
        }

        // Сегмент 2: K -> M
        for (std::size_t i = 0; i < points_per_segment; ++i) {
            double alpha = static_cast<double>(i) / points_per_segment;
            double kx = k_x_K + alpha * (k_x_M - k_x_K);
            double ky = k_y_K + alpha * (k_y_M - k_y_K);
            path.push_back(evaluate(kx, ky));
        }

        // Сегмент 3: M -> Gamma
        for (std::size_t i = 0; i < points_per_segment; ++i) {
            double alpha = static_cast<double>(i) / points_per_segment;
            double kx = k_x_M + alpha * (0.0 - k_x_M);
            double ky = k_y_M + alpha * (0.0 - k_y_M);
            path.push_back(evaluate(kx, ky));
        }

        return path;
    }
};

int main() {
    GrapheneBandModel model(2.8, 1.42);
    auto k_path = model.compute_high_symmetry_path(150);

    std::cout << "Обчислено " << k_path.size() << " точок уздовж шляху Gamma-K-M-Gamma.\n";
    std::cout << "Точка Gamma (k=0): E = " << k_path.front().e_cond << " еВ\n";
    
    return 0;
}
