//
// three_body.cpp — Чисельне інтегрування задачі трьох тіл мовою C++20
// Ідіоматична реалізація з RAII, std::array, векторною алгеброю та шаблонами
//

#include <iostream>
#include <array>
#include <cmath>
#include <iomanip>
#include <concepts>

namespace celestial {

// Шаблонна структура 3D-вектора
template <typename T = double>
struct Vector3 {
    T x{0.0}, y{0.0}, z{0.0};

    constexpr Vector3 operator+(const Vector3& rhs) const noexcept {
        return {x + rhs.x, y + rhs.y, z + rhs.z};
    }
    constexpr Vector3 operator-(const Vector3& rhs) const noexcept {
        return {x - rhs.x, y - rhs.y, z - rhs.z};
    }
    constexpr Vector3 operator*(T scalar) const noexcept {
        return {x * scalar, y * scalar, z * scalar};
    }
    constexpr Vector3& operator+=(const Vector3& rhs) noexcept {
        x += rhs.x; y += rhs.y; z += rhs.z;
        return *this;
    }
    [[nodiscard]] double norm_sq() const noexcept {
        return x * x + y * y + z * z;
    }
    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(norm_sq());
    }
};

// Тіло в гравітаційній системі
struct CelestialBody {
    double mass{1.0};
    Vector3<double> pos{};
    Vector3<double> vel{};
    Vector3<double> acc{};
};

template <std::size_t N = 3>
class ThreeBodySystem {
public:
    static constexpr double G = 1.0;
    static constexpr double softening_sq = 1e-12;

    explicit ThreeBodySystem(const std::array<CelestialBody, N>& initial_bodies)
        : bodies_(initial_bodies) {}

    // Обчислення прискорень для всіх тіл (закони Ньютона)
    void update_accelerations() noexcept {
        for (auto& body : bodies_) {
            body.acc = {0.0, 0.0, 0.0};
        }

        for (std::size_t i = 0; i < N; ++i) {
            for (std::size_t j = i + 1; j < N; ++j) {
                Vector3<double> dr = bodies_[j].pos - bodies_[i].pos;
                double dist_sq = dr.norm_sq() + softening_sq;
                double dist = std::sqrt(dist_sq);
                double inv_dist3 = 1.0 / (dist_sq * dist);

                bodies_[i].acc += dr * (G * bodies_[j].mass * inv_dist3);
                bodies_[j].acc += dr * (-G * bodies_[i].mass * inv_dist3);
            }
        }
    }

    // Сімплектичний крок інтегратора Йошиди 4-го порядку
    void step_yoshida4(double dt) noexcept {
        static constexpr std::array<double, 4> c{
            0.5 * 1.3512071919596578,
            0.5 * (1.3512071919596578 - 1.7024143839193153),
            0.5 * (1.3512071919596578 - 1.7024143839193153),
            0.5 * 1.3512071919596578
        };
        static constexpr std::array<double, 3> d{
            1.3512071919596578,
            -1.7024143839193153,
            1.3512071919596578
        };

        for (std::size_t step = 0; step < 4; ++step) {
            for (auto& body : bodies_) {
                body.pos += body.vel * (c[step] * dt);
            }
            if (step < 3) {
                update_accelerations();
                for (auto& body : bodies_) {
                    body.vel += body.acc * (d[step] * dt);
                }
            }
        }
    }

    // Розрахунок повної механічної енергії E
    [[nodiscard]] double total_energy() const noexcept {
        double kinetic = 0.0;
        double potential = 0.0;

        for (std::size_t i = 0; i < N; ++i) {
            kinetic += 0.5 * bodies_[i].mass * bodies_[i].vel.norm_sq();
            for (std::size_t j = i + 1; j < N; ++j) {
                double dist = (bodies_[j].pos - bodies_[i].pos).norm();
                potential -= (G * bodies_[i].mass * bodies_[j].mass) / dist;
            }
        }
        return kinetic + potential;
    }

    [[nodiscard]] const std::array<CelestialBody, N>& bodies() const noexcept {
        return bodies_;
    }

private:
    std::array<CelestialBody, N> bodies_;
};

} // namespace celestial

int main() {
    using namespace celestial;

    // Початкові умови: орбіта-вісімка (Figure-Eight choreography)
    const std::array<CelestialBody, 3> figure_eight_setup{{
        {1.0, {-0.97000436,  0.24308753, 0.0}, { 0.46620531,  0.43236573, 0.0}, {}},
        {1.0, { 0.97000436, -0.24308753, 0.0}, { 0.46620531,  0.43236573, 0.0}, {}},
        {1.0, { 0.0,         0.0,        0.0}, {-0.93241062, -0.86473146, 0.0}, {}}
    }};

    ThreeBodySystem<3> system(figure_eight_setup);
    const double initial_energy = system.total_energy();
    const double dt = 0.001;
    const int total_steps = 10000;

    std::cout << std::fixed << std::setprecision(10);
    std::cout << "=== Симуляція задачі трьох тіл (C++20 / Yoshida 4) ===\n";
    std::cout << "Початкова енергія E0 = " << initial_energy << "\n";

    for (int k = 1; k <= total_steps; ++k) {
        system.step_yoshida4(dt);

        if (k % 2000 == 0) {
            double current_energy = system.total_energy();
            double rel_err = std::abs((current_energy - initial_energy) / initial_energy);
            std::cout << "Крок " << std::setw(5) << k
                      << " | E = " << current_energy
                      << " | Відносна похибка E: " << std::scientific << rel_err << std::defaultfloat << "\n";
        }
    }

    return 0;
}
