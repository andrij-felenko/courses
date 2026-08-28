#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>

struct CircuitPoint {
    double x{0.0};
    double y{0.0};
    double v{0.0};          // Потенціал у точці
    double sigma_s{0.0};    // Поверхнева густина заряду
};

struct FieldPoint {
    double x{0.0};
    double y{0.0};
    double Ex{0.0};
    double Ey{0.0};
    double Bz{0.0};
    double Sx{0.0};
    double Sy{0.0};
};

class CircuitPoyntingSimulator {
public:
    constexpr static double EPSILON_0 = 8.8541878128e-12;
    constexpr static double MU_0 = 4.0 * std::numbers::pi * 1e-7;

    CircuitPoyntingSimulator(std::size_t num_points, double width, double height, 
                             double v0, double current, double wire_radius)
        : current_{current}, v0_{v0}, r_wire_{wire_radius}, n_pts_{num_points} {
        
        points_.resize(num_points);
        const double perimeter = 2.0 * (width + height);
        const double geom_factor = (2.0 * std::numbers::pi * EPSILON_0) / (r_wire_ * std::log(perimeter / r_wire_));

        for (std::size_t i = 0; i < num_points; ++i) {
            double s = (static_cast<double>(i) / num_points) * perimeter;
            
            if (s < width) {
                points_[i].x = s - width / 2.0;
                points_[i].y = height / 2.0;
            } else if (s < width + height) {
                points_[i].x = width / 2.0;
                points_[i].y = height / 2.0 - (s - width);
            } else if (s < 2.0 * width + height) {
                points_[i].x = width / 2.0 - (s - (width + height));
                points_[i].y = -height / 2.0;
            } else {
                points_[i].x = -width / 2.0;
                points_[i].y = -height / 2.0 + (s - (2.0 * width + height));
            }

            double frac = static_cast<double>(i) / num_points;
            points_[i].v = (0.5 - frac) * v0_;
            points_[i].sigma_s = geom_factor * points_[i].v;
        }
    }

    [[nodiscard]] FieldPoint computeFields(double px, double py) const {
        FieldPoint fp{.x = px, .y = py};
        constexpr double softening = 1e-4;
        const double ds = (2.0 * (0.4 + 0.2)) / static_cast<double>(n_pts_);

        for (const auto& pt : points_) {
            double rx = px - pt.x;
            double ry = py - pt.y;
            double r2 = rx * rx + ry * ry + softening * softening;
            double r = std::sqrt(r2);

            double dq = pt.sigma_s * (2.0 * std::numbers::pi * r_wire_) * ds;
            double dE = dq / (4.0 * std::numbers::pi * EPSILON_0 * r2);
            fp.Ex += dE * (rx / r);
            fp.Ey += dE * (ry / r);

            double dB = (MU_0 * current_) / (2.0 * std::numbers::pi * r);
            fp.Bz += dB;
        }

        fp.Sx = (fp.Ey * fp.Bz) / MU_0;
        fp.Sy = (-fp.Ex * fp.Bz) / MU_0;

        return fp;
    }

private:
    std::vector<CircuitPoint> points_;
    double current_{0.0};
    double v0_{0.0};
    double r_wire_{0.0};
    std::size_t n_pts_{0};
};

int main() {
    constexpr std::size_t N_POINTS = 400;
    constexpr double V0 = 12.0;
    constexpr double R_LOAD = 6.0;
    constexpr double I_CURRENT = V0 / R_LOAD;
    constexpr double R_WIRE = 0.001;

    CircuitPoyntingSimulator sim(N_POINTS, 0.4, 0.2, V0, I_CURRENT, R_WIRE);
    FieldPoint fp = sim.computeFields(0.19, 0.0);

    std::cout << std::scientific << std::setprecision(3);
    std::cout << "=== Симуляція полів у колі зі струмом (C++) ===\n";
    std::cout << "ЕРС: " << V0 << " V, Струм: " << I_CURRENT << " A\n";
    std::cout << "Точка спостереження поблизу резистора (0.19 м, 0.0 м):\n";
    std::cout << "  Ex: " << fp.Ex << " В/м, Ey: " << fp.Ey << " В/м\n";
    std::cout << "  Bz: " << fp.Bz << " Тл\n";
    std::cout << "  Вектор Пойнтінга Sx: " << fp.Sx << " Вт/м², Sy: " << fp.Sy << " Вт/м²\n";

    return 0;
}
