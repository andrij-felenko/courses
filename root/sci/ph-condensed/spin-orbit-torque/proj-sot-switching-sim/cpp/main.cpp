#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <numbers>

// Структура фізичних параметрів гетероструктури SOT
struct SotParameters {
    double Ms = 1.0e6;          // Намагніченість насичення (А/м)
    double Hk_eff = 4.0e5;      // Ефективне поле анізотропії PMA (А/м)
    double Bx = 0.05;           // Допоміжне поле вздовж осі x (Тесла)
    double alpha = 0.02;        // Загасання Гільберта
    double theta_SH = 0.30;     // Кут спинового Холла (наприклад, β-W)
    double d_fm = 1.2e-9;       // Товщина феромагнітного шару (м)
    double Jc = 1.2e11;         // Густина струму запису (А/м²)
};

// Векторний трійка 3D
using Vector3D = std::array<double, 3>;

// Векторний добуток u × v
constexpr Vector3D crossProduct(const Vector3D& u, const Vector3D& v) noexcept {
    return {
        u[1] * v[2] - u[2] * v[1],
        u[2] * v[0] - u[0] * v[2],
        u[0] * v[1] - u[1] * v[0]
    };
}

// Нормалізація вектора |m| = 1
constexpr Vector3D normalize(const Vector3D& v) noexcept {
    const double norm = std::sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
    return { v[0] / norm, v[1] / norm, v[2] / norm };
}

// Фізичні константи
namespace Constants {
    constexpr double hbar = 1.054571817e-34;  // Дж·с
    constexpr double elem_charge = 1.602176634e-19; // Кл
    constexpr double mu0 = 4.0 * std::numbers::pi * 1.0e-7; // Гн/м
    constexpr double gamma_bar = 1.7608596e11; // Рад/(с·Тл)
}

// Обчислення правої частини d m / d t
Vector3D computeLLGS(const Vector3D& m, const SotParameters& p, bool current_on) noexcept {
    // 1. Внутрішнє ефективне поле H_eff (А/м)
    const double Hx_ext = p.Bx / Constants::mu0;
    const Vector3D Heff = {
        Hx_ext,
        0.0,
        p.Hk_eff * m[2]
    };

    // 2. Амплитуда SOT полів
    const double H_DL = current_on ? (Constants::hbar * p.theta_SH * p.Jc) / 
                                     (2.0 * Constants::elem_charge * p.Ms * p.d_fm) : 0.0;
    
    // Спінова поляризація σ = (0, 1, 0)
    const Vector3D sigma = { 0.0, 1.0, 0.0 };

    // 3. Компоненти LLGS
    const Vector3D m_cross_Heff = crossProduct(m, Heff);
    const Vector3D m_cross_m_cross_Heff = crossProduct(m, m_cross_Heff);
    
    const Vector3D m_cross_sigma = crossProduct(m, sigma);
    const Vector3D m_cross_m_cross_sigma = crossProduct(m, m_cross_sigma);

    const double gamma_mu0 = Constants::gamma_bar * Constants::mu0;
    const double factor = 1.0 / (1.0 + p.alpha * p.alpha);

    Vector3D dmdt;
    for (std::size_t i = 0; i < 3; ++i) {
        const double precession = -gamma_mu0 * m_cross_Heff[i];
        const double damping = -gamma_mu0 * p.alpha * m_cross_m_cross_Heff[i];
        const double sot_dl = gamma_mu0 * H_DL * m_cross_m_cross_sigma[i];
        const double sot_fl = p.alpha * gamma_mu0 * H_DL * m_cross_sigma[i];

        dmdt[i] = factor * (precession + damping + sot_dl + sot_fl);
    }

    return dmdt;
}

int main() {
    SotParameters params;
    
    // Параметри інтегрування
    const double dt = 1.0e-13;        // Крок 0.1 пс
    const double t_pulse = 1.0e-9;     // Тривалість струмового імпульсу 1 нс
    const double t_total = 2.0e-9;     // Загальний час розрахунку 2 нс
    const std::size_t steps = static_cast<std::size_t>(t_total / dt);

    // Початковий стан: m_z ≈ +1 із малим похилом
    Vector3D m = normalize({ 0.05, 0.0, 0.9987 });

    std::cout << "Starting SOT Switching Simulation (C++)..." << std::endl;
    std::cout << "Time (ns) \t m_x \t\t m_y \t\t m_z" << std::endl;
    std::cout << "--------------------------------------------------------" << std::endl;

    for (std::size_t step = 0; step <= steps; ++step) {
        const double time = step * dt;
        const bool current_on = (time <= t_pulse);

        if (step % 2000 == 0) {
            std::cout << std::fixed << std::setprecision(3) << (time * 1.0e9) << " ns \t "
                      << std::setprecision(4) << m[0] << " \t " << m[1] << " \t " << m[2] << std::endl;
        }

        // Крок Runge-Kutta 4th order (RK4)
        const Vector3D k1 = computeLLGS(m, params, current_on);
        
        Vector3D m_k2;
        for (std::size_t i = 0; i < 3; ++i) m_k2[i] = m[i] + 0.5 * dt * k1[i];
        const Vector3D k2 = computeLLGS(m_k2, params, current_on);

        Vector3D m_k3;
        for (std::size_t i = 0; i < 3; ++i) m_k3[i] = m[i] + 0.5 * dt * k2[i];
        const Vector3D k3 = computeLLGS(m_k3, params, current_on);

        Vector3D m_k4;
        for (std::size_t i = 0; i < 3; ++i) m_k4[i] = m[i] + dt * k3[i];
        const Vector3D k4 = computeLLGS(m_k4, params, current_on);

        for (std::size_t i = 0; i < 3; ++i) {
            m[i] += (dt / 6.0) * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]);
        }

        m = normalize(m);
    }

    std::cout << "--------------------------------------------------------" << std::endl;
    std::cout << "Simulation finished. Final m_z: " << m[2] << std::endl;
    return 0;
}
