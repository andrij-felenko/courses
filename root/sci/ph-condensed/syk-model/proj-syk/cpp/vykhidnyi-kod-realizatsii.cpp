// C++17 ідіоматична реалізація ітераційного солуера Швінгера-Дайсона
#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <memory>

class SYKSolverCPP {
public:
    using Complex = std::complex<double>;

    SYKSolverCPP(std::size_t pts, double beta, double J, double alpha)
        : m_pts(pts), m_beta(beta), m_J(J), m_alpha(alpha),
          m_G_omega(pts), m_Sigma_omega(pts), m_G_tau(pts), m_Sigma_tau(pts) 
    {
        const double pi = std::acos(-1.0);
        for (std::size_t n = 0; n < m_pts; ++n) {
            double omega_n = (2.0 * static_cast<double>(n) + 1.0 - static_cast<double>(m_pts)) * pi / m_beta;
            m_G_omega[n] = Complex(0.0, -1.0 / omega_n);
            m_Sigma_omega[n] = Complex(0.0, 0.0);
        }
    }

    void step() {
        const double pi = std::acos(-1.0);
        const double dt = m_beta / static_cast<double>(m_pts);

        // Обчислення G(tau) та Sigma(tau)
        for (std::size_t k = 0; k < m_pts; ++k) {
            double tau = (static_cast<double>(k) + 0.5) * dt;
            Complex g_val(0.0, 0.0);
            for (std::size_t n = 0; n < m_pts; ++n) {
                double omega_n = (2.0 * static_cast<double>(n) + 1.0 - static_cast<double>(m_pts)) * pi / m_beta;
                g_val += m_G_omega[n] * std::exp(Complex(0.0, -omega_n * tau)) / m_beta;
            }
            m_G_tau[k] = g_val.real();
            m_Sigma_tau[k] = m_J * m_J * std::pow(m_G_tau[k], 3);
        }

        // Обчислення Sigma(omega) та оновлення G(omega)
        for (std::size_t n = 0; n < m_pts; ++n) {
            double omega_n = (2.0 * static_cast<double>(n) + 1.0 - static_cast<double>(m_pts)) * pi / m_beta;
            Complex sig_val(0.0, 0.0);
            for (std::size_t k = 0; k < m_pts; ++k) {
                double tau = (static_cast<double>(k) + 0.5) * dt;
                sig_val += m_Sigma_tau[k] * std::exp(Complex(0.0, omega_n * tau)) * dt;
            }
            m_Sigma_omega[n] = sig_val;

            Complex G_new = 1.0 / (Complex(0.0, omega_n) - m_Sigma_omega[n]);
            m_G_omega[n] = (1.0 - m_alpha) * m_G_omega[n] + m_alpha * G_new;
        }
    }

    double get_G_tau(std::size_t idx) const { return m_G_tau.at(idx); }

private:
    std::size_t m_pts;
    double m_beta;
    double m_J;
    double m_alpha;
    std::vector<Complex> m_G_omega;
    std::vector<Complex> m_Sigma_omega;
    std::vector<double> m_G_tau;
    std::vector<double> m_Sigma_tau;
};

int main() {
    constexpr std::size_t N_pts = 64;
    constexpr double beta = 10.0;
    constexpr double J = 1.0;
    constexpr double alpha = 0.2;

    auto solver = std::make_unique<SYKSolverCPP>(N_pts, beta, J, alpha);
    std::cout << "Розпочато чисельний розв'язок рівнянь Швінгера-Дайсона (C++)...\n";

    for (int iter = 0; iter < 50; ++iter) {
        solver->step();
    }

    std::cout << "Розв'язок успішно досягнуто! G(tau=beta/2) = " << solver->get_G_tau(N_pts / 2) << "\n";
    return 0;
}
