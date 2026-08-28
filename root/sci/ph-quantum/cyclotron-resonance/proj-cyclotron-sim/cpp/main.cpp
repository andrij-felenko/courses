#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <complex>
#include <iomanip>
#include <numbers>

struct SimParams {
    double m_eff { 0.067 * 9.109e-31 }; // GaAs (0.067 m0)
    double q     { -1.602e-19 };
    double B     { 0.25 };              // 0.25 Тл
    double E0    { 100.0 };             // 100 В/м
    double tau   { 1.0e-11 };           // 10 пс
    double dt    { 1.0e-14 };           // 10 фс
    std::size_t steps { 500000 };
};

class CyclotronSimulator {
public:
    explicit CyclotronSimulator(SimParams params)
        : p_(params),
          gen_(std::random_device{}()),
          dis_unit_(0.0, 1.0),
          dis_angle_(0.0, 2.0 * std::numbers::pi) {}

    [[nodiscard]] double simulate_absorption(double omega) {
        std::complex<double> v { 0.0, 0.0 };
        double total_work = 0.0;
        
        const double p_coll = 1.0 - std::exp(-p_.dt / p_.tau);
        const double v_th = std::sqrt(2.0 * 1.38e-23 * 4.2 / p_.m_eff);

        for (std::size_t i = 0; i < p_.steps; ++i) {
            const double t = static_cast<double>(i) * p_.dt;
            
            // Вектор поля у комплексній формі: E = E0 * exp(i * w * t)
            const std::complex<double> E { p_.E0 * std::cos(omega * t), p_.E0 * std::sin(omega * t) };
            
            // Лоренцівський розгін у комплексній площині: a = (q/m*) * (E - i*B*v)
            const std::complex<double> a = (p_.q / p_.m_eff) * (E - std::complex<double>(0.0, p_.B) * v);
            
            v += a * p_.dt;
            
            // Поглинута миттєва потужність: P = q * Re(v * conj(E))
            const double power = p_.q * (v.real() * E.real() + v.imag() * E.imag());
            total_work += power * p_.dt;
            
            // Випадкове фононне розсіювання
            if (dis_unit_(gen_) < p_coll) {
                const double theta = dis_angle_(gen_);
                v = std::complex<double>(v_th * std::cos(theta), v_th * std::sin(theta));
            }
        }
        
        return total_work / (static_cast<double>(p_.steps) * p_.dt);
    }

    [[nodiscard]] double cyclotron_frequency() const noexcept {
        return std::abs(p_.q * p_.B / p_.m_eff);
    }

private:
    SimParams p_;
    std::mt19937 gen_;
    std::uniform_real_distribution<double> dis_unit_;
    std::uniform_real_distribution<double> dis_angle_;
};

int main() {
    SimParams params;
    CyclotronSimulator sim(params);
    
    const double wc = sim.cyclotron_frequency();
    std::cout << "Циклотронна частота fc = " << std::fixed << std::setprecision(3) 
              << (wc / (2.0 * std::numbers::pi * 1e9)) << " GHz\n";
    std::cout << "Параметр чистоти wc * tau = " << (wc * params.tau) << "\n\n";

    std::cout << std::setw(10) << "f (GHz)" << " | " << std::setw(18) << "P_abs (W)\n";
    std::cout << "-------------------------------------\n";

    for (double f_ghz = 50.0; f_ghz <= 150.0; f_ghz += 5.0) {
        const double omega = 2.0 * std::numbers::pi * f_ghz * 1e9;
        const double p_abs = sim.simulate_absorption(omega);
        std::cout << std::setw(10) << f_ghz << " | " 
                  << std::scientific << std::setprecision(4) << std::setw(18) << p_abs << "\n";
    }

    return 0;
}
