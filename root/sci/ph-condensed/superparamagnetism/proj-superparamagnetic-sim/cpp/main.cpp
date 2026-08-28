#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <iomanip>

struct Vec3 {
    double x{0.0}, y{0.0}, z{0.0};

    [[nodiscard]] Vec3 cross(const Vec3& o) const noexcept {
        return {y * o.z - z * o.y, z * o.x - x * o.z, x * o.y - y * o.x};
    }

    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(x * x + y * y + z * z);
    }

    [[nodiscard]] Vec3 normalized() const noexcept {
        const double n = norm();
        const double inv = (n < 1e-15) ? 1.0 : (1.0 / n);
        return {x * inv, y * inv, z * inv};
    }

    Vec3& operator+=(const Vec3& o) noexcept {
        x += o.x; y += o.y; z += o.z;
        return *this;
    }
};

inline Vec3 operator*(double s, const Vec3& v) noexcept {
    return {s * v.x, s * v.y, s * v.z};
}

inline Vec3 operator+(const Vec3& a, const Vec3& b) noexcept {
    return {a.x + b.x, a.y + b.y, a.z + b.z};
}

class MacrospinSimulator {
public:
    struct Params {
        double Ms{1.4e6};           // Насичена намагніченість, А/м
        double Ku{4.5e5};           // Анізотропія, Дж/м3
        double diameter{8.0e-9};    // Діаметр наночастинки, м
        double alpha{0.1};          // Затухання Ґільберта
        double T{300.0};            // Температура, К
    };

    explicit MacrospinSimulator(Params p)
        : p_(p),
          volume_((M_PI / 6.0) * std::pow(p.diameter, 3)),
          gamma_prime_(1.76e11 / (1.0 + p.alpha * p.alpha)),
          Hk_(2.0 * p.Ku / p.Ms),
          stdev_h_th_(std::sqrt((2.0 * p.alpha * 1.380649e-23 * p.T) / (1.76e11 * p.Ms * volume_))),
          gen_(std::random_device{}()) {}

    struct SimulationResult {
        double total_time_sec;
        std::size_t flip_count;
        double tau_theoretical_sec;
        double final_mz;
    };

    SimulationResult run(double dt_sec, std::size_t num_steps) {
        Vec3 m{0.0, 0.0, 1.0};
        std::size_t flips = 0;
        int state = 1;
        const double inv_sqrt_dt = 1.0 / std::sqrt(dt_sec);

        for (std::size_t step = 0; step < num_steps; ++step) {
            Vec3 h_th{
                stdev_h_th_ * dist_(gen_) * inv_sqrt_dt,
                stdev_h_th_ * dist_(gen_) * inv_sqrt_dt,
                stdev_h_th_ * dist_(gen_) * inv_sqrt_dt
            };

            Vec3 h_eff = h_th + Vec3{0.0, 0.0, Hk_ * m.z};

            // Метод Хена (Стратонович)
            Vec3 k1 = sllg_rhs(m, h_eff);
            Vec3 m_pred = (m + dt_sec * k1).normalized();

            Vec3 h_eff_pred = h_th + Vec3{0.0, 0.0, Hk_ * m_pred.z};
            Vec3 k2 = sllg_rhs(m_pred, h_eff_pred);

            m = (m + (0.5 * dt_sec) * (k1 + k2)).normalized();

            if (state == 1 && m.z < -0.2) {
                state = -1;
                ++flips;
            } else if (state == -1 && m.z > 0.2) {
                state = 1;
                ++flips;
            }
        }

        const double kb = 1.380649e-23;
        const double tau_th = 1.0e-9 * std::exp((p_.Ku * volume_) / (kb * p_.T));
        return {num_steps * dt_sec, flips, tau_th, m.z};
    }

private:
    [[nodiscard]] Vec3 sllg_rhs(const Vec3& m, const Vec3& h_eff) const noexcept {
        Vec3 m_x_h = m.cross(h_eff);
        Vec3 m_x_m_x_h = m.cross(m_x_h);
        return (-1.0 * gamma_prime_) * m_x_h + (-1.0 * p_.alpha * gamma_prime_) * m_x_m_x_h;
    }

    Params p_;
    double volume_;
    double gamma_prime_;
    double Hk_;
    double stdev_h_th_;
    std::mt19937 gen_;
    std::normal_distribution<double> dist_{0.0, 1.0};
};

int main() {
    MacrospinSimulator::Params p;
    p.diameter = 8.0e-9;
    p.T = 300.0;

    MacrospinSimulator sim(p);
    const double dt = 1.0e-13;
    const std::size_t steps = 5'000'000;

    std::cout << "=== Стохастична LLG симуляція макроспіна (C++17) ===\n";
    auto res = sim.run(dt, steps);

    std::cout << std::scientific << std::setprecision(3);
    std::cout << "Час моделювання: " << res.total_time_sec << " s\n";
    std::cout << "Перевертань макроспіна: " << res.flip_count << "\n";
    std::cout << "Теоретичний час Нееля-Брауна: " << res.tau_theoretical_sec << " s\n";

    return 0;
}
