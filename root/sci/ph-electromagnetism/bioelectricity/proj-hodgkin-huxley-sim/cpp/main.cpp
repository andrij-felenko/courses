#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>

class HodgkinHuxleyNeuron {
public:
    struct State {
        double V = -65.0; // Напруга мембрани (мВ)
        double m = 0.05;  // Натрієва активація
        double h = 0.60;  // Натрієва інактивація
        double n = 0.32;  // Калієва активація
    };

    explicit HodgkinHuxleyNeuron(double V_rest = -65.0) {
        state_.V = V_rest;
        initializeGatingAtRest(V_rest);
    }

    // Інтегрування воріт за точною схемою Раша-Ларсена
    void step(double I_ext_uA_cm2, double dt_ms) {
        const double V = state_.V;
        const double m = state_.m;
        const double h = state_.h;
        const double n = state_.n;

        const double I_Na = g_Na_max_ * (m * m * m) * h * (V - E_Na_);
        const double I_K  = g_K_max_ * (n * n * n * n) * (V - E_K_);
        const double I_L  = g_L_ * (V - E_L_);

        const double dVdt = (I_ext_uA_cm2 - I_Na - I_K - I_L) / C_m_;
        state_.V += dVdt * dt_ms;

        updateGatingVariable(state_.m, alphaM(V), betaM(V), dt_ms);
        updateGatingVariable(state_.h, alphaH(V), betaH(V), dt_ms);
        updateGatingVariable(state_.n, alphaN(V), betaN(V), dt_ms);
    }

    [[nodiscard]] const State& getState() const noexcept { return state_; }

private:
    static constexpr double C_m_ = 1.0;
    static constexpr double g_Na_max_ = 120.0;
    static constexpr double g_K_max_ = 36.0;
    static constexpr double g_L_ = 0.3;
    static constexpr double E_Na_ = 50.0;
    static constexpr double E_K_ = -77.0;
    static constexpr double E_L_ = -54.387;

    State state_;

    static void updateGatingVariable(double& y, double alpha, double beta, double dt) noexcept {
        const double sum = alpha + beta;
        const double y_inf = alpha / sum;
        const double tau = 1.0 / sum;
        y = y_inf + (y - y_inf) * std::exp(-dt / tau);
    }

    static double alphaM(double V) {
        const double x = V + 40.0;
        return (std::abs(x) < 1e-6) ? 1.0 : (0.1 * x / (1.0 - std::exp(-x / 10.0)));
    }

    static double betaM(double V) {
        return 4.0 * std::exp(-(V + 65.0) / 18.0);
    }

    static double alphaH(double V) {
        return 0.07 * std::exp(-(V + 65.0) / 20.0);
    }

    static double betaH(double V) {
        return 1.0 / (1.0 + std::exp(-(V + 35.0) / 10.0));
    }

    static double alphaN(double V) {
        const double x = V + 55.0;
        return (std::abs(x) < 1e-6) ? 0.1 : (0.01 * x / (1.0 - std::exp(-x / 10.0)));
    }

    static double betaN(double V) {
        return 0.125 * std::exp(-(V + 65.0) / 80.0);
    }

    void initializeGatingAtRest(double V_rest) {
        const double a_m = alphaM(V_rest);
        const double b_m = betaM(V_rest);
        const double a_h = alphaH(V_rest);
        const double b_h = betaH(V_rest);
        const double a_n = alphaN(V_rest);
        const double b_n = betaN(V_rest);

        state_.m = a_m / (a_m + b_m);
        state_.h = a_h / (a_h + b_h);
        state_.n = a_n / (a_n + b_n);
    }
};

int main() {
    HodgkinHuxleyNeuron neuron(-65.0);
    constexpr double dt = 0.01;
    constexpr double t_max = 50.0;

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "# Time(ms)\tVoltage(mV)\tm\th\tn\n";

    for (double t = 0.0; t <= t_max; t += dt) {
        const double I_ext = (t >= 10.0 && t <= 12.0) ? 10.0 : 0.0;
        
        if (static_cast<int>(t / dt) % 100 == 0) {
            const auto& s = neuron.getState();
            std::cout << t << "\t\t" << s.V << "\t\t" 
                      << std::setprecision(3) << s.m << "\t" << s.h << "\t" << s.n << "\n";
        }

        neuron.step(I_ext, dt);
    }

    return 0;
}
