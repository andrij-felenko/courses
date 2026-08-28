#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>

struct PhasePoint {
    double q{0.0};
    double p{0.0};
};

class PhaseEnsemble {
public:
    explicit PhaseEnsemble(std::size_t count, double radius, double center_q = 1.0, double center_p = 0.0) {
        m_points.reserve(count);
        for (std::size_t i = 0; i < count; ++i) {
            double angle = 2.0 * std::numbers::pi * i / count;
            m_points.push_back({center_q + radius * std::cos(angle), center_p + radius * std::sin(angle)});
        }
    }

    [[nodiscard]] double calculate_phase_area() const noexcept {
        double area = 0.0;
        const std::size_t n = m_points.size();
        for (std::size_t i = 0; i < n; ++i) {
            std::size_t j = (i + 1) % n;
            area += (m_points[i].q * m_points[j].p) - (m_points[i].p * m_points[j].q);
        }
        return 0.5 * std::abs(area);
    }

    void step_explicit_euler(double dt) noexcept {
        for (auto& pt : m_points) {
            double q_next = pt.q + pt.p * dt;
            double p_next = pt.p - pt.q * dt;
            pt.q = q_next;
            pt.p = p_next;
        }
    }

    void step_implicit_euler(double dt) noexcept {
        const double denom = 1.0 + dt * dt;
        for (auto& pt : m_points) {
            double q_next = (pt.q + dt * pt.p) / denom;
            double p_next = (pt.p - dt * pt.q) / denom;
            pt.q = q_next;
            pt.p = p_next;
        }
    }

    void step_symplectic_euler(double dt) noexcept {
        for (auto& pt : m_points) {
            pt.p -= pt.q * dt;       // Оновлення імпульсу
            pt.q += pt.p * dt;       // Оновлення координати з новим імпульсом
        }
    }

private:
    std::vector<PhasePoint> m_points;
};

int main() {
    constexpr std::size_t particles = 500;
    constexpr double dt = 0.05;
    constexpr int total_steps = 1000;

    PhaseEnsemble explicit_ens(particles, 0.2);
    PhaseEnsemble implicit_ens(particles, 0.2);
    PhaseEnsemble symplectic_ens(particles, 0.2);

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "Початкова площа фазової хмари: " << symplectic_ens.calculate_phase_area() << "\n\n";
    std::cout << std::setw(5) << "Крок" << " | "
              << std::setw(14) << "Явний Ейлер" << " | "
              << std::setw(14) << "Неявний Ейлер" << " | "
              << std::setw(14) << "Симплектичний" << "\n";
    std::cout << "-------------------------------------------------------\n";

    for (int step = 1; step <= total_steps; ++step) {
        explicit_ens.step_explicit_euler(dt);
        implicit_ens.step_implicit_euler(dt);
        symplectic_ens.step_symplectic_euler(dt);

        if (step % 200 == 0) {
            std::cout << std::setw(5) << step << " | "
                      << std::setw(14) << explicit_ens.calculate_phase_area() << " | "
                      << std::setw(14) << implicit_ens.calculate_phase_area() << " | "
                      << std::setw(14) << symplectic_ens.calculate_phase_area() << "\n";
        }
    }

    return 0;
}
