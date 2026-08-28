#include <iostream>
#include <iomanip>
#include <vector>
#include <cmath>
#include <array>
#include <numbers>

struct TunnelDiode {
    double ip{0.005};    // Піковий струм, А (5 мА)
    double vp{0.065};    // Пікова напруга, В (65 мВ)
    double iv{0.0005};   // Струм западини, А (0.5 мА)
    double vv{0.350};    // Напруга западини, В (350 мВ)
    double vf{0.500};    // Напруга відновлення, В (500 мВ)
    double cj{4.0e-12};  // Бар'єрна ємність, Ф (4 пФ)
    double rs{1.5};      // Опір втрат, Ом (1.5 Ом)
    double ls{0.4e-9};   // Паразитна індуктивність, Гн (0.4 нГн)

    [[nodiscard]] double current(double v) const noexcept {
        if (v < 0.0) {
            return v / (vp / ip);
        }
        const double i_tu = ip * (v / vp) * std::exp(1.0 - (v / vp));
        constexpr double a_coeff = 4.0;
        double i_ex = (v < vv) ? (iv * (v / vv))
                               : (iv * std::exp(a_coeff * (v - vv)) / (1.0 + std::exp(a_coeff * (v - vv))));
        constexpr double ut = 0.02585;
        const double i_diff = 1e-11 * (std::exp(v / (1.3 * ut)) - 1.0);
        return i_tu + i_ex + i_diff;
    }
};

struct Circuit {
    double e_bias{0.220}; // 220 мВ напруга зміщення
    double r_load{40.0};  // 40 Ом навантажувальний опір
};

struct State {
    double v_j{0.052};  // Напруга p-n переходу, В
    double i_l{0.0042}; // Струм індуктивності, А

    constexpr State operator+(const State& rhs) const noexcept {
        return {v_j + rhs.v_j, i_l + rhs.i_l};
    }

    constexpr State operator*(double scalar) const noexcept {
        return {v_j * scalar, i_l * scalar};
    }
};

class Simulator {
public:
    Simulator(TunnelDiode diode, Circuit circuit)
        : m_diode(diode), m_circuit(circuit) {}

    [[nodiscard]] static double input_pulse(double t) noexcept {
        constexpr double t_start = 100e-12; // 100 пс затримка
        constexpr double t_rise  = 20e-12;  // 20 пс фронт запуску
        constexpr double v_step  = 0.050;   // 50 мВ амплітуда запуску
        if (t < t_start) return 0.0;
        if (t < t_start + t_rise) {
            return v_step * (t - t_start) / t_rise;
        }
        return v_step;
    }

    [[nodiscard]] State derivatives(double t, const State& s) const noexcept {
        const double v_total = m_circuit.e_bias + input_pulse(t);
        const double i_dio = m_diode.current(s.v_j);
        
        const double dv_dt = (s.i_l - i_dio) / m_diode.cj;
        const double di_dt = (v_total - s.i_l * (m_circuit.r_load + m_diode.rs) - s.v_j) / m_diode.ls;
        
        return {dv_dt, di_dt};
    }

    void run(double t_end, double dt) {
        double t = 0.0;
        State s{};
        
        const double v_10 = 0.052 + 0.10 * (0.480 - 0.052);
        const double v_90 = 0.052 + 0.90 * (0.480 - 0.052);
        double t_10 = -1.0, t_90 = -1.0;

        std::cout << "# Симуляція перемикання пікосекундного тригера на тунельному діоді (C++20)\n";
        std::cout << "# Час(пс)\tНапруга(В)\tСтрум(мА)\tВхід(В)\n";
        std::cout << std::fixed << std::setprecision(4);

        int step = 0;
        while (t <= t_end) {
            if (step % 50 == 0) {
                std::cout << std::setw(8) << t * 1e12 << "\t"
                          << std::setw(8) << s.v_j << "\t"
                          << std::setw(8) << s.i_l * 1e3 << "\t"
                          << std::setw(8) << input_pulse(t) << "\n";
            }

            if (t_10 < 0.0 && s.v_j >= v_10) t_10 = t;
            if (t_90 < 0.0 && s.v_j >= v_90) t_90 = t;

            // 4 кроки методу Рунге-Кутти
            const auto k1 = derivatives(t, s);
            const auto k2 = derivatives(t + 0.5 * dt, s + k1 * (0.5 * dt));
            const auto k3 = derivatives(t + 0.5 * dt, s + k2 * (0.5 * dt));
            const auto k4 = derivatives(t + dt, s + k3 * dt);

            s = s + (k1 + k2 * 2.0 + k3 * 2.0 + k4) * (dt / 6.0);
            t += dt;
            step++;
        }

        if (t_10 > 0.0 && t_90 > 0.0) {
            std::cout << "# Розрахований час наростання фронту t_r (10%-90%): "
                      << std::setprecision(2) << (t_90 - t_10) * 1e12 << " пс\n";
        }
    }

private:
    TunnelDiode m_diode;
    Circuit m_circuit;
};

int main() {
    Simulator sim{TunnelDiode{}, Circuit{}};
    sim.run(800e-12, 0.1e-12);
    return 0;
}
