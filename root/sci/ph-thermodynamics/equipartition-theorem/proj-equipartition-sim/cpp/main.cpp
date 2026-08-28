#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <numeric>
#include <iomanip>

struct Vec2 {
    double x{0.0};
    double y{0.0};

    constexpr Vec2 operator+(const Vec2& o) const noexcept { return {x + o.x, y + o.y}; }
    constexpr Vec2 operator-(const Vec2& o) const noexcept { return {x - o.x, y - o.y}; }
    constexpr Vec2 operator*(double s) const noexcept { return {x * s, y * s}; }
    constexpr double dot(const Vec2& o) const noexcept { return x * o.x + y * o.y; }
    constexpr double norm_sq() const noexcept { return x * x + y * y; }
    double norm() const noexcept { return std::sqrt(norm_sq()); }
};

struct DiatomicMolecule {
    Vec2 r1, r2; // Позиції атомів
    Vec2 v1, v2; // Швидкості атомів
    Vec2 f1, f2; // Сили
    double m1{1.0};
    double m2{1.0};
    double r0{1.0};  // Рівноважна відстань
    double k_spring{100.0}; // Жорсткість
};

class EquipartitionSimulation {
public:
    EquipartitionSimulation(std::size_t num_molecules, double dt)
        : dt_(dt) {
        molecules_.reserve(num_molecules);
        std::mt19937 gen(42);
        std::normal_distribution<double> dist_v(0.0, 2.0);

        for (std::size_t i = 0; i < num_molecules; ++i) {
            DiatomicMolecule m;
            double center_x = static_cast<double>(i % 10) * 4.0;
            double center_y = static_cast<double>(i / 10) * 4.0;
            m.r1 = {center_x - 0.5 * m.r0, center_y};
            m.r2 = {center_x + 0.5 * m.r0, center_y};

            // Непорівну розподілені початкові швидкості для перевірки релаксації
            m.v1 = {dist_v(gen) * 3.0, dist_v(gen) * 0.2};
            m.v2 = {dist_v(gen) * 3.0, dist_v(gen) * 0.2};
            molecules_.push_back(m);
        }
        compute_forces();
    }

    void step() {
        // 1. Оновлення координат та напівкрок швидкості
        for (auto& m : molecules_) {
            m.v1 = m.v1 + m.f1 * (0.5 * dt_ / m.m1);
            m.v2 = m.v2 + m.f2 * (0.5 * dt_ / m.m2);
            m.r1 = m.r1 + m.v1 * dt_;
            m.r2 = m.r2 + m.v2 * dt_;
        }

        // 2. Обчислення нових сил у оновлених позиціях
        compute_forces();

        // 3. Другий напівкрок швидкості
        for (auto& m : molecules_) {
            m.v1 = m.v1 + m.f1 * (0.5 * dt_ / m.m1);
            m.v2 = m.v2 + m.f2 * (0.5 * dt_ / m.m2);
        }
    }

    struct EnergyReport {
        double avg_e_trans{0.0};
        double avg_e_rot{0.0};
        double avg_e_vib{0.0};
    };

    [[nodiscard]] EnergyReport sample_energies() const {
        double total_trans = 0.0;
        double total_rot = 0.0;
        double total_vib = 0.0;

        for (const auto& m : molecules_) {
            const double M = m.m1 + m.m2;
            const Vec2 v_cm = (m.v1 * m.m1 + m.v2 * m.m2) * (1.0 / M);
            const double e_trans = 0.5 * M * v_cm.norm_sq();

            const Vec2 r_rel = m.r2 - m.r1;
            const double dist = r_rel.norm();
            const Vec2 n = r_rel * (1.0 / (dist > 1e-9 ? dist : 1.0));

            const Vec2 v_rel = m.v2 - m.v1;
            const double v_vib = v_rel.dot(n);
            const double v_rot = v_rel.x * n.y - v_rel.y * n.x;

            const double mu = (m.m1 * m.m2) / M;
            const double e_vib = 0.5 * mu * v_vib * v_vib + 0.5 * m.k_spring * (dist - m.r0) * (dist - m.r0);
            const double e_rot = 0.5 * mu * v_rot * v_rot;

            total_trans += e_trans;
            total_rot += e_rot;
            total_vib += e_vib;
        }

        const double inv_n = 1.0 / static_cast<double>(molecules_.size());
        return {total_trans * inv_n, total_rot * inv_n, total_vib * inv_n};
    }

private:
    void compute_forces() {
        for (auto& m : molecules_) {
            const Vec2 r_rel = m.r2 - m.r1;
            const double dist = r_rel.norm();
            const double dr = dist - m.r0;
            const Vec2 n = r_rel * (1.0 / (dist > 1e-9 ? dist : 1.0));

            const Vec2 f_spring = n * (m.k_spring * dr);
            m.f1 = f_spring;
            m.f2 = f_spring * (-1.0);
        }
    }

    double dt_{0.001};
    std::vector<DiatomicMolecule> molecules_;
};

int main() {
    EquipartitionSimulation sim(100, 0.001);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Крок\tE_trans\tE_rot\tE_vib\tE_total\n";

    for (int step = 0; step <= 5000; ++step) {
        sim.step();
        if (step % 1000 == 0) {
            auto report = sim.sample_energies();
            double e_tot = report.avg_e_trans + report.avg_e_rot + report.avg_e_vib;
            std::cout << step << "\t"
                      << report.avg_e_trans << "\t"
                      << report.avg_e_rot << "\t"
                      << report.avg_e_vib << "\t"
                      << e_tot << "\n";
        }
    }
    return 0;
}
