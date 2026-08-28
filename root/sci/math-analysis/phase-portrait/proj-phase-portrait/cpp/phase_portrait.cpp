// phase_portrait.cpp — Обчислювальний двигун фазового простору мовою C++ (C++20)
#include <iostream>
#include <fstream>
#include <vector>
#include <array>
#include <cmath>
#include <functional>
#include <string_view>
#include <filesystem>

namespace phase {

// Стан у 2D фазовому просторі
struct State {
    double q{0.0};
    double p{0.0};

    [[nodiscard]] constexpr State operator+(const State& rhs) const noexcept {
        return {q + rhs.q, p + rhs.p};
    }

    [[nodiscard]] constexpr State operator*(double scalar) const noexcept {
        return {q * scalar, p * scalar};
    }
};

// Тип векторного поля: функція, що приймає стан і повертає похідні (dq/dt, dp/dt)
using VectorField = std::function<State(const State&)>;

// Клас інтегратора фазових траєкторій
class RK4Integrator {
public:
    explicit RK4Integrator(VectorField field) : field_(std::move(field)) {}

    // Виконати один крок RK4
    [[nodiscard]] State step(const State& current, double h) const {
        const State k1 = field_(current);
        const State k2 = field_(current + k1 * (0.5 * h));
        const State k3 = field_(current + k2 * (0.5 * h));
        const State k4 = field_(current + k3 * h);

        return current + (k1 + k2 * 2.0 + k3 * 2.0 + k4) * (h / 6.0);
    }

    // Симуляція повної траєкторії із збереженням у вектор
    [[nodiscard]] std::vector<State> integrate(State initial, double h, std::size_t steps) const {
        std::vector<State> trajectory;
        trajectory.reserve(steps + 1);
        State current = initial;
        trajectory.push_back(current);

        for (std::size_t i = 0; i < steps; ++i) {
            current = step(current, h);
            trajectory.push_back(current);
        }
        return trajectory;
    }

private:
    VectorField field_;
};

// RAII Експортер даних фазового портрета у файл
class PhaseDataExporter {
public:
    explicit PhaseDataExporter(std::string_view filepath) : file_(filepath.data()) {
        if (!file_.is_open()) {
            throw std::runtime_error("Не вдалося відкрити файл для експорту даних");
        }
    }

    void write_header() {
        file_ << "step,t,q,p\n";
    }

    void write_trajectory(const std::vector<State>& traj, double h) {
        for (std::size_t i = 0; i < traj.size(); ++i) {
            file_ << i << "," << (i * h) << "," << traj[i].q << "," << traj[i].p << "\n";
        }
    }

private:
    std::ofstream file_;
};

// Генератор нелінійного осцилятора Ван дер Поля: dq/dt = p, dp/dt = mu*(1 - q^2)*p - q
inline VectorField make_van_der_pol(double mu) {
    return [mu](const State& s) -> State {
        return {
            s.p,
            mu * (1.0 - s.q * s.q) * s.p - s.q
        };
    };
}

} // namespace phase

int main() {
    try {
        constexpr double mu = 1.5; // Коефіцієнт нелінійності Ван дер Поля
        const auto vdp_field = phase::make_van_der_pol(mu);
        const phase::RK4Integrator integrator(vdp_field);

        constexpr double h = 0.005;
        constexpr std::size_t steps = 4000;

        // 1. Початковий стан усередині циклу (зростає назовні)
        const phase::State inner_start{0.1, 0.1};
        const auto inner_traj = integrator.integrate(inner_start, h, steps);

        phase::PhaseDataExporter inner_file("vdp_inner.csv");
        inner_file.write_header();
        inner_file.write_trajectory(inner_traj, h);

        // 2. Початковий стан зовні циклу (спадає всередину)
        const phase::State outer_start{3.0, 2.5};
        const auto outer_traj = integrator.integrate(outer_start, h, steps);

        phase::PhaseDataExporter outer_file("vdp_outer.csv");
        outer_file.write_header();
        outer_file.write_trajectory(outer_traj, h);

        std::cout << "Успішно обчислено граничний цикл Ван дер Поля (mu = " << mu << ").\n";
    }
    catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
