// duffing_sim.cpp — Обчислювальний клас та переріз Пуанкаре на сучасній C++20
#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <numbers>
#include <stdexcept>

struct DuffingParams {
    double alpha{ -1.0 };
    double beta{   1.0 };
    double delta{  0.2 };
    double gamma{  0.3 };
    double omega{  1.2 };
};

struct Point2D {
    double x{ 0.0 };
    double v{ 0.0 };
};

class DuffingSolver {
public:
    explicit DuffingSolver(DuffingParams params) : params_(params) {}

    [[nodiscard]] Point2D rk4Step(Point2D s, double t, double h) const noexcept {
        const auto k1 = derivatives(s, t);
        const auto k2 = derivatives({ s.x + 0.5 * h * k1.x, s.v + 0.5 * h * k1.v }, t + 0.5 * h);
        const auto k3 = derivatives({ s.x + 0.5 * h * k2.x, s.v + 0.5 * h * k2.v }, t + 0.5 * h);
        const auto k4 = derivatives({ s.x + h * k3.x,       s.v + h * k3.v },       t + h);

        return {
            s.x + (h / 6.0) * (k1.x + 2.0 * k2.x + 2.0 * k3.x + k4.x),
            s.v + (h / 6.0) * (k1.v + 2.0 * k2.v + 2.0 * k3.v + k4.v)
        };
    }

    [[nodiscard]] std::vector<Point2D> generatePoincareSection(
        Point2D initialState,
        std::size_t transientPeriods,
        std::size_t poincarePoints,
        std::size_t stepsPerPeriod) const 
    {
        std::vector<Point2D> poincareData;
        poincareData.reserve(poincarePoints);

        const double period = 2.0 * std::numbers::pi / params_.omega;
        const double h = period / static_cast<double>(stepsPerPeriod);
        
        Point2D state = initialState;
        double t = 0.0;

        // Пропуск перехідного процесу (transient)
        const std::size_t totalTransientSteps = transientPeriods * stepsPerPeriod;
        for (std::size_t i = 0; i < totalTransientSteps; ++i) {
            state = rk4Step(state, t, h);
            t += h;
        }

        // Стробоскопічний відбір точок
        for (std::size_t i = 0; i < poincarePoints; ++i) {
            poincareData.push_back(state);
            for (std::size_t step = 0; step < stepsPerPeriod; ++step) {
                state = rk4Step(state, t, h);
                t += h;
            }
        }

        return poincareData;
    }

private:
    [[nodiscard]] Point2D derivatives(Point2D s, double t) const noexcept {
        return {
            s.v,
            -params_.delta * s.v - params_.alpha * s.x - params_.beta * s.x * s.x * s.x + params_.gamma * std::cos(params_.omega * t)
        };
    }

    DuffingParams params_;
};

int main() {
    try {
        DuffingParams params{ .alpha = -1.0, .beta = 1.0, .delta = 0.2, .gamma = 0.3, .omega = 1.2 };
        DuffingSolver solver(params);

        const auto poincarePoints = solver.generatePoincareSection({ 0.1, 0.0 }, 200, 2000, 500);

        std::ofstream outFile("poincare_cpp.dat");
        if (!outFile) {
            throw std::runtime_error("Не вдалося створити файл poincare_cpp.dat");
        }

        for (const auto& [x, v] : poincarePoints) {
            outFile << x << "\t" << v << "\n";
        }

        std::cout << "Успішно збережено " << poincarePoints.size() << " точок перерізу Пуанкаре (C++20)\n";
    }
    catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
