#include <iostream>
#include <complex>
#include <array>
#include <cmath>
#include <iomanip>

class SpinorState {
public:
    using Complex = std::complex<double>;

    SpinorState(Complex alpha, Complex beta) : state_{alpha, beta} {
        normalize();
    }

    [[nodiscard]] Complex alpha() const noexcept { return state_[0]; }
    [[nodiscard]] Complex beta() const noexcept { return state_[1]; }

    [[nodiscard]] double expectation_sx() const noexcept {
        return (std::conj(state_[0]) * state_[1]).real();
    }

    [[nodiscard]] double expectation_sy() const noexcept {
        return (std::conj(state_[0]) * state_[1]).imag();
    }

    [[nodiscard]] double expectation_sz() const noexcept {
        return 0.5 * (std::norm(state_[0]) - std::norm(state_[1]));
    }

    void advance_rk4(const std::array<double, 3>& B, double gamma, double dt) {
        auto deriv = [gamma, &B](const std::array<Complex, 2>& s) -> std::array<Complex, 2> {
            const Complex i_unit(0.0, 1.0);
            const Complex Bx_minus_iBy(B[0], -B[1]);
            const Complex Bx_plus_iBy(B[0], B[1]);

            Complex da = -i_unit * (0.5 * gamma) * (B[2] * s[0] + Bx_minus_iBy * s[1]);
            Complex db = -i_unit * (0.5 * gamma) * (Bx_plus_iBy * s[0] - B[2] * s[1]);
            return {da, db};
        };

        auto k1 = deriv(state_);
        
        std::array<Complex, 2> s_k2 = {
            state_[0] + 0.5 * dt * k1[0],
            state_[1] + 0.5 * dt * k1[1]
        };
        auto k2 = deriv(s_k2);

        std::array<Complex, 2> s_k3 = {
            state_[0] + 0.5 * dt * k2[0],
            state_[1] + 0.5 * dt * k2[1]
        };
        auto k3 = deriv(s_k3);

        std::array<Complex, 2> s_k4 = {
            state_[0] + dt * k3[0],
            state_[1] + dt * k3[1]
        };
        auto k4 = deriv(s_k4);

        state_[0] += (dt / 6.0) * (k1[0] + 2.0 * k2[0] + 2.0 * k3[0] + k4[0]);
        state_[1] += (dt / 6.0) * (k1[1] + 2.0 * k2[1] + 2.0 * k3[1] + k4[1]);
        normalize();
    }

private:
    void normalize() noexcept {
        double norm = std::sqrt(std::norm(state_[0]) + std::norm(state_[1]));
        if (norm > 1e-12) {
            state_[0] /= norm;
            state_[1] /= norm;
        }
    }

    std::array<Complex, 2> state_;
};

int main() {
    using namespace std::complex_literals;

    // Initial spin state along +x
    SpinorState spinor(1.0 / std::sqrt(2.0), 1.0 / std::sqrt(2.0));
    std::array<double, 3> B_field = {0.0, 0.0, 1.0}; // 1 Tesla along Z
    constexpr double gamma_e = 1.7608596e11; // rad / (s * T)
    constexpr double dt = 1e-13;
    constexpr int steps = 100;

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "Time (ps) | <Sx>       | <Sy>       | <Sz>\n";
    std::cout << "---------------------------------------------\n";

    for (int step = 0; step <= steps; ++step) {
        if (step % 10 == 0) {
            double time_ps = step * dt * 1e12;
            std::cout << std::setw(9) << time_ps << " | "
                      << std::setw(10) << spinor.expectation_sx() << " | "
                      << std::setw(10) << spinor.expectation_sy() << " | "
                      << std::setw(10) << spinor.expectation_sz() << "\n";
        }
        spinor.advance_rk4(B_field, gamma_e, dt);
    }
    return 0;
}
