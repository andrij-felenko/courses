#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <numeric>

struct FerroelectricMaterial {
    double alpha{-1.0}; // α < 0 у сегнетофазі
    double beta{1.0};   // β > 0
    double gamma{0.1};  // коефіцієнт релаксації
    double e_amplitude{1.5};
    double frequency{1.0};
    double e_bias{0.0};
};

struct DataPoint {
    double time;
    double e_field;
    double polarization;
};

class HysteresisSimulator {
public:
    explicit HysteresisSimulator(FerroelectricMaterial mat) : mat_(mat) {}

    [[nodiscard]] std::pair<std::vector<DataPoint>, double> simulate(double dt, std::size_t total_steps) const {
        std::vector<DataPoint> result;
        result.reserve(total_steps / 2);

        double t = 0.0;
        double p = 0.1;
        double energy_loss = 0.0;

        for (std::size_t i = 0; i < total_steps; ++i) {
            const double e_field = mat_.e_amplitude * std::sin(2.0 * std::numbers::pi * mat_.frequency * t) + mat_.e_bias;
            
            if (i >= total_steps / 2) {
                result.push_back({t, e_field, p});
                if (result.size() > 1) {
                    const auto& prev = result[result.size() - 2];
                    const double dp = p - prev.polarization;
                    const double avg_e = 0.5 * (e_field + prev.e_field);
                    energy_loss += avg_e * dp;
                }
            }

            p = step_rk4(t, p, dt);
            t += dt;
        }
        return {result, energy_loss};
    }

private:
    [[nodiscard]] double rk4_derivative(double t, double p) const {
        const double e_field = mat_.e_amplitude * std::sin(2.0 * std::numbers::pi * mat_.frequency * t) + mat_.e_bias;
        const double df_dp = mat_.alpha * p + mat_.beta * std::pow(p, 3) - e_field;
        return -df_dp / mat_.gamma;
    }

    [[nodiscard]] double step_rk4(double t, double p, double dt) const {
        const double k1 = rk4_derivative(t, p);
        const double k2 = rk4_derivative(t + 0.5 * dt, p + 0.5 * dt * k1);
        const double k3 = rk4_derivative(t + 0.5 * dt, p + 0.5 * dt * k2);
        const double k4 = rk4_derivative(t + dt, p + dt * k3);
        return p + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4);
    }

    FerroelectricMaterial mat_;
};

int main() {
    FerroelectricMaterial mat;
    HysteresisSimulator simulator(mat);
    const auto [data, loss] = simulator.simulate(0.0005, 4000);

    std::cout << "Отримано точок петлі: " << data.size() << "\n";
    std::cout << "Розрахована площа петлі (втрати W): " << loss << " Дж/м3\n";
    return 0;
}
