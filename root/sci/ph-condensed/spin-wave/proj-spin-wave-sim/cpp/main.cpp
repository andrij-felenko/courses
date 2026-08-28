#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>
#include <iomanip>

// Структура тривимірного спінового вектора
struct Vector3 {
    double x{0.0};
    double y{0.0};
    double z{1.0};

    double norm() const {
        return std::sqrt(x * x + y * y + z * z);
    }

    void normalize() {
        double len = norm();
        if (len > 1e-12) {
            x /= len;
            y /= len;
            z /= len;
        }
    }
};

// Векторні операції
Vector3 operator+(const Vector3& a, const Vector3& b) {
    return {a.x + b.x, a.y + b.y, a.z + b.z};
}

Vector3 operator*(double scalar, const Vector3& v) {
    return {scalar * v.x, scalar * v.y, scalar * v.z};
}

Vector3 cross(const Vector3& a, const Vector3& b) {
    return {
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

class SpinChainSimulator {
public:
    SpinChainSimulator(std::size_t num_spins, double exchange_J, double ext_field_B0, double damping_alpha)
        : N_(num_spins), J_(exchange_J), B0_(ext_field_B0), alpha_base_(damping_alpha), spins_(num_spins), alpha_profile_(num_spins, damping_alpha) {
        for (auto& s : spins_) {
            s = {0.0, 0.0, 1.0}; // Основний стан ↑
        }

        // Поглинаючі граничні шари (PML) на краях ланцюжка для запобігання відбиттю
        std::size_t pml_width = N_ / 10;
        for (std::size_t i = 0; i < pml_width; ++i) {
            double factor = std::pow(static_cast<double>(pml_width - i) / pml_width, 2.0);
            alpha_profile_[i] += 0.5 * factor;
            alpha_profile_[N_ - 1 - i] += 0.5 * factor;
        }
    }

    // Додавання гаусового збудження у центрі ланцюжка
    void excite_gaussian_pulse(double amplitude, double sigma) {
        std::size_t center = N_ / 2;
        for (std::size_t i = 0; i < N_; ++i) {
            double dist = static_cast<double>(i) - static_cast<double>(center);
            double pulse = amplitude * std::exp(-dist * dist / (2.0 * sigma * sigma));
            spins_[i].x += pulse;
            spins_[i].normalize();
        }
    }

    // Обчислення правої частини рівняння LLG для спіна i
    Vector3 compute_ds_dt(std::size_t i, const std::vector<Vector3>& state) const {
        Vector3 s = state[i];
        
        // Сусідні спіни із зафіксованими граничними умовами
        Vector3 s_prev = (i > 0) ? state[i - 1] : state[i];
        Vector3 s_next = (i < N_ - 1) ? state[i + 1] : state[i];

        // Ефективне поле: зовнішнє B0 + обмінне J*(S_prev + S_next)
        Vector3 B_eff = {
            J_ * (s_prev.x + s_next.x),
            J_ * (s_prev.y + s_next.y),
            B0_ + J_ * (s_prev.z + s_next.z)
        };

        Vector3 prec = cross(s, B_eff);
        Vector3 damp = cross(s, prec);

        double alpha = alpha_profile_[i];
        double gamma_prime = 1.0 / (1.0 + alpha * alpha);
        return (-1.0 * gamma_prime) * prec + (-alpha * gamma_prime) * damp;
    }

    // Крок інтегрування методом Рунге-Кутти 4-го порядку (RK4)
    void step(double dt) {
        std::vector<Vector3> k1(N_), k2(N_), k3(N_), k4(N_);
        std::vector<Vector3> temp(N_);

        // K1
        for (std::size_t i = 0; i < N_; ++i) k1[i] = compute_ds_dt(i, spins_);

        // K2
        for (std::size_t i = 0; i < N_; ++i) temp[i] = spins_[i] + (0.5 * dt) * k1[i];
        for (std::size_t i = 0; i < N_; ++i) k2[i] = compute_ds_dt(i, temp);

        // K3
        for (std::size_t i = 0; i < N_; ++i) temp[i] = spins_[i] + (0.5 * dt) * k2[i];
        for (std::size_t i = 0; i < N_; ++i) k3[i] = compute_ds_dt(i, temp);

        // K4
        for (std::size_t i = 0; i < N_; ++i) temp[i] = spins_[i] + dt * k3[i];
        for (std::size_t i = 0; i < N_; ++i) k4[i] = compute_ds_dt(i, temp);

        // Оновлення стану та ренормування
        for (std::size_t i = 0; i < N_; ++i) {
            spins_[i] = spins_[i] + (dt / 6.0) * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]);
            spins_[i].normalize();
        }
    }

    const std::vector<Vector3>& get_spins() const { return spins_; }

private:
    std::size_t N_;
    double J_;
    double B0_;
    double alpha_base_;
    std::vector<Vector3> spins_;
    std::vector<double> alpha_profile_;
};

int main() {
    constexpr std::size_t NUM_SPINS = 250;
    constexpr double J_EXCHANGE = 1.0;
    constexpr double B_EXTERNAL = 0.2;
    constexpr double DAMPING = 0.005; // Низьке згасання для магноніки
    constexpr double DT = 0.02;
    constexpr std::size_t STEPS = 600;

    SpinChainSimulator sim(NUM_SPINS, J_EXCHANGE, B_EXTERNAL, DAMPING);
    sim.excite_gaussian_pulse(0.25, 6.0);

    std::cout << "# Спіновий ланцюжок: N=" << NUM_SPINS << ", J=" << J_EXCHANGE 
              << ", B0=" << B_EXTERNAL << ", steps=" << STEPS << std::endl;

    for (std::size_t step = 0; step <= STEPS; ++step) {
        if (step % 100 == 0) {
            const auto& spins = sim.get_spins();
            double avg_sx = 0.0;
            for (const auto& s : spins) avg_sx += std::abs(s.x);
            avg_sx /= NUM_SPINS;

            std::cout << "Step " << std::setw(4) << step 
                      << " | <|Sx|> = " << std::fixed << std::setprecision(5) << avg_sx 
                      << " | Sx[center] = " << spins[NUM_SPINS / 2].x << std::endl;
        }
        sim.step(DT);
    }

    return 0;
}
