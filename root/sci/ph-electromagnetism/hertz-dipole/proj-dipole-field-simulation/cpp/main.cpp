#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <span>

class HertzDipoleSimulator {
public:
    struct FieldPoint {
        double r_m;
        double theta_rad;
        double E_r;
        double E_theta;
        double H_phi;
        double S_r;
    };

    static constexpr double c_speed = 299792458.0;
    static constexpr double epsilon_0 = 8.8541878128e-12;

    HertzDipoleSimulator(double frequency_hz, double current_A, double length_m)
        : freq_(frequency_hz), I0_(current_A), dl_(length_m) {
        omega_ = 2.0 * std::numbers::pi * freq_;
        k_ = omega_ / c_speed;
        lambda_ = c_speed / freq_;
    }

    [[nodiscard]] FieldPoint calculate(double r, double theta, double t) const {
        const double ret_t = t - r / c_speed;
        const double phase = omega_ * ret_t;

        const double cos_p = std::cos(phase);
        const double sin_p = std::sin(phase);
        const double sin_th = std::sin(theta);
        const double cos_th = std::cos(theta);

        const double r2 = r * r;
        const double r3 = r2 * r;
        const double k2 = k_ * k_;

        const double E_coeff = (I0_ * dl_) / (4.0 * std::numbers::pi * epsilon_0 * omega_);
        const double H_coeff = (I0_ * dl_) / (4.0 * std::numbers::pi);

        FieldPoint pt{};
        pt.r_m = r;
        pt.theta_rad = theta;
        pt.E_r = 2.0 * E_coeff * cos_th * (cos_p / r3 - k_ * sin_p / r2);
        pt.E_theta = E_coeff * sin_th * (cos_p / r3 - k_ * sin_p / r2 - k2 * cos_p / r);
        pt.H_phi = H_coeff * sin_th * (sin_p / r2 + k_ * cos_p / r);
        pt.S_r = pt.E_theta * pt.H_phi;

        return pt;
    }

    [[nodiscard]] double wave_length() const noexcept { return lambda_; }

private:
    double freq_;
    double I0_;
    double dl_;
    double omega_;
    double k_;
    double lambda_;
};

int main() {
    constexpr double frequency = 100e6; // 100 MHz
    constexpr double current = 1.0;     // 1 A
    
    HertzDipoleSimulator sim(frequency, current, 0.03); // dl = 0.03m

    std::cout << std::scientific << std::setprecision(4);
    std::cout << "Дипольний розрахунок на частоті " << frequency / 1e6 << " МГц\n";

    const std::vector<double> r_multipliers = {0.01, 0.1, 0.159, 0.5, 1.0, 5.0};
    for (double mult : r_multipliers) {
        const double r = mult * sim.wave_length();
        auto res = sim.calculate(r, std::numbers::pi / 2.0, 0.0);
        std::cout << "r/lambda = " << mult 
                  << " | E_theta = " << res.E_theta 
                  << " | H_phi = " << res.H_phi 
                  << " | S_r = " << res.S_r << "\n";
    }

    return 0;
}
