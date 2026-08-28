// Implementation in C++ (C++20 standard)
#include <iostream>
#include <vector>
#include <fstream>
#include <cmath>
#include <numbers>
#include <span>
#include <concepts>
#include <expected>

namespace poincare {

struct State {
    double x{0.0};
    double v{0.0};
};

struct SystemParameters {
    double gamma{0.2};
    double f0{0.3};
    double omega{1.0};
};

enum class SectionError {
    FileOpenFailure,
    IntegrationDivergence,
    InvalidParameters
};

class DuffingSystem {
public:
    explicit DuffingSystem(SystemParameters params) : params_(params) {}

    [[nodiscard]] constexpr State rhs(State s, double t) const noexcept {
        return {
            .x = s.v,
            .v = -params_.gamma * s.v + s.x - s.x * s.x * s.x + params_.f0 * std::cos(params_.omega * t)
        };
    }

    [[nodiscard]] State rk4_step(State s, double t, double dt) const noexcept {
        const auto k1 = rhs(s, t);
        const auto k2 = rhs({s.x + 0.5 * dt * k1.x, s.v + 0.5 * dt * k1.v}, t + 0.5 * dt);
        const auto k3 = rhs({s.x + 0.5 * dt * k2.x, s.v + 0.5 * dt * k2.v}, t + 0.5 * dt);
        const auto k4 = rhs({s.x + dt * k3.x, s.v + dt * k3.v}, t + dt);

        return {
            s.x + (dt / 6.0) * (k1.x + 2.0 * k2.x + 2.0 * k3.x + k4.x),
            s.v + (dt / 6.0) * (k1.v + 2.0 * k2.v + 2.0 * k3.v + k4.v)
        };
    }

    [[nodiscard]] State interpolate(State s1, State s2, double t1, double dt, double t_target) const noexcept {
        const double s = (t_target - t1) / dt;
        const auto v1 = rhs(s1, t1);
        const auto v2 = rhs(s2, t1 + dt);

        const double h00 = (1.0 - 3.0 * s * s + 2.0 * s * s * s);
        const double h10 = s * (1.0 - s) * (1.0 - s);
        const double h01 = s * s * (3.0 - 2.0 * s);
        const double h11 = s * s * (s - 1.0);

        return {
            h00 * s1.x + h10 * dt * v1.x + h01 * s2.x + h11 * dt * v1.x,
            h00 * s1.v + h10 * dt * v1.v + h01 * s2.v + h11 * dt * v2.v
        };
    }

    [[nodiscard]] double period() const noexcept {
        return 2.0 * std::numbers::pi / params_.omega;
    }

private:
    SystemParameters params_;
};

class SectionCollector {
public:
    explicit SectionCollector(DuffingSystem sys) : system_(std::move(sys)) {}

    std::expected<std::vector<State>, SectionError> compute_section(
        State initial_state, 
        std::size_t transient_periods, 
        std::size_t num_points, 
        std::size_t steps_per_period) 
    {
        if (steps_per_period == 0 || num_points == 0) {
            return std::unexpected(SectionError::InvalidParameters);
        }

        const double T = system_.period();
        const double dt = T / static_cast<double>(steps_per_period);

        State state = initial_state;
        double t = 0.0;

        // Пропускаємо перехідний режим (transient response)
        for (std::size_t i = 0; i < transient_periods * steps_per_period; ++i) {
            state = system_.rk4_step(state, t, dt);
            t += dt;
            if (std::isnan(state.x) || std::isnan(state.v)) {
                return std::unexpected(SectionError::IntegrationDivergence);
            }
        }

        std::vector<State> section_points;
        section_points.reserve(num_points);

        double next_cross_time = t + T;

        while (section_points.size() < num_points) {
            State next_state = system_.rk4_step(state, t, dt);
            double next_t = t + dt;

            if (t <= next_cross_time && next_t > next_cross_time) {
                State exact = system_.interpolate(state, next_state, t, dt, next_cross_time);
                section_points.push_back(exact);
                next_cross_time += T;
            }

            state = next_state;
            t = next_t;
        }

        return section_points;
    }

private:
    DuffingSystem system_;
};

} // namespace poincare

int main() {
    using namespace poincare;

    SystemParameters params{ .gamma = 0.2, .f0 = 0.3, .omega = 1.0 };
    DuffingSystem system(params);
    SectionCollector collector(system);

    State start{ .x = 0.1, .v = 0.0 };
    auto result = collector.compute_section(start, 1000, 5000, 500);

    if (!result) {
        std::cerr << "Помилка обчислення перерізу Пуанкаре!\n";
        return 1;
    }

    std::ofstream out("poincare_cpp.dat");
    if (!out.is_open()) {
        std::cerr << "Не вдалося відкрити файл poincare_cpp.dat\n";
        return 1;
    }

    for (const auto& pt : *result) {
        out << pt.x << "\t" << pt.v << "\n";
    }

    std::cout << "Успішно обчислено " << result->size() << " точок перерізу Пуанкаре (C++20).\n";
    return 0;
}
