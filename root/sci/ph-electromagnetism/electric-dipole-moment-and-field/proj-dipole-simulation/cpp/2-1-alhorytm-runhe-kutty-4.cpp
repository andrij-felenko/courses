#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>

// Стан ротатора: кут theta (рад) та кутова швидкість omega (рад/с)
struct State {
    double theta;
    double omega;
};

// Права частина системи ODE: dtheta/dt = omega, domega/dt = (-p*E*sin(theta) - gamma*omega) / I
State derivatives(const State& s, double p, double E, double I, double gamma) {
    double dtheta = s.omega;
    double domega = (-p * E * std::sin(s.theta) - gamma * s.omega) / I;
    return {dtheta, domega};
}

// Крок інтегрування методом Рунге-Кутти 4-го порядку (RK4)
State rk4_step(const State& current, double dt, double p, double E, double I, double gamma) {
    const auto k1 = derivatives(current, p, E, I, gamma);

    const State s2{current.theta + 0.5 * dt * k1.theta, current.omega + 0.5 * dt * k1.omega};
    const auto k2 = derivatives(s2, p, E, I, gamma);

    const State s3{current.theta + 0.5 * dt * k2.theta, current.omega + 0.5 * dt * k2.omega};
    const auto k3 = derivatives(s3, p, E, I, gamma);

    const State s4{current.theta + dt * k3.theta, current.omega + dt * k3.omega};
    const auto k4 = derivatives(s4, p, E, I, gamma);

    const double dtheta = (k1.theta + 2.0 * k2.theta + 2.0 * k3.theta + k4.theta) / 6.0;
    const double domega = (k1.omega + 2.0 * k2.omega + 2.0 * k3.omega + k4.omega) / 6.0;

    return {current.theta + dt * dtheta, current.omega + dt * domega};
}

int main() {
    // Параметри мікромолекулярного ротатора (молекула H2O)
    const double p = 1.85 * 3.33564e-30; // p = 1.85 D
    const double E = 1e6;                // Поле E = 1 МВ/м
    const double I = 2.0e-47;            // Момент інерції кг*м^2
    const double gamma = 1.0e-36;        // Коефіцієнт в'язкого згасання

    State state{1.57079632679, 0.0};     // Стартовий кут 90 градусів (pi/2)
    const double dt = 1e-14;             // Крок часу 10 фемтосекунд
    const int steps = 500;

    std::cout << "--- Симуляція згасаючих коливань диполя (RK4) ---\n";
    std::cout << std::setw(10) << "Час (пс)" << std::setw(15) << "Кут (град)" 
              << std::setw(20) << "Швидкість (рад/с)\n";

    for (int i = 0; i <= steps; ++i) {
        if (i % 50 == 0) {
            double time_ps = i * dt * 1e12;
            double angle_deg = state.theta * 180.0 / std::numbers::pi;
            std::cout << std::setw(10) << time_ps << std::setw(15) << angle_deg 
                      << std::setw(20) << state.omega << "\n";
        }
        state = rk4_step(state, dt, p, E, I, gamma);
    }

    return 0;
}
