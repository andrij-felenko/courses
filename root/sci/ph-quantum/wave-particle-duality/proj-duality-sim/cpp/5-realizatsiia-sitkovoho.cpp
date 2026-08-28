#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>

using Complex = std::complex<double>;

int main() {
    const size_t N = 300;               // Кількість вузлів просторової сітки
    const double dx = 1.0e-11;          // Крок сітки (0.01 нм)
    const double dt = 1.0e-18;          // Часовий крок (1 аттосекунда)
    const double m_e = 9.109383e-31;    // Маса електрона (кг)
    const double hbar = 1.054571e-34;   // Зведена стала Планка

    // Комплексний множник дискретизації сітки
    const Complex alpha(0.0, (hbar * dt) / (2.0 * m_e * dx * dx));
    
    std::vector<Complex> psi(N, 0.0);
    std::vector<double> V(N, 0.0);       // Потенціальний профіль V(x)
    
    // Створення потенціального бар'єра у центрі сітки (E_barrier = 10 eV)
    double barrier_start = 160 * dx;
    double barrier_end = 170 * dx;
    double barrier_height_J = 10.0 * 1.602176e-19; // 10 eV в Джоулях
    
    for (size_t i = 0; i < N; ++i) {
        double x = i * dx;
        if (x >= barrier_start && x <= barrier_end) {
            V[i] = barrier_height_J;
        }
    }
    
    // Ініціалізація Ґаусового пакета ліворуч від бар'єра
    double x0 = 80 * dx;
    double sigma0 = 1.5e-10;  // Початковий розмір (0.15 нм)
    double E_kin_eV = 12.0;   // Кінетична енергія (12 eV > 10 eV)
    double E_kin_J = E_kin_eV * 1.602176e-19;
    double k0 = std::sqrt(2.0 * m_e * E_kin_J) / hbar;
    
    for (size_t i = 0; i < N; ++i) {
        double x = i * dx;
        double env = std::exp(- (x - x0) * (x - x0) / (4.0 * sigma0 * sigma0));
        psi[i] = env * std::complex<double>(std::cos(k0 * x), std::sin(k0 * x));
    }
    
    std::cout << "=== Сіткове моделювання еволюції та тунелювання хвильового пакета ===\n";
    std::cout << "Кінетична енергія пакета: " << E_kin_eV << " eV | Висота бар'єра: 10.0 eV\n\n";
    
    // Часова еволюція на 6000 кроків
    for (size_t step = 0; step <= 6000; ++step) {
        if (step % 2000 == 0) {
            double prob_sum = 0.0;
            double mean_x = 0.0;
            for (size_t i = 0; i < N; ++i) {
                double p = std::norm(psi[i]);
                prob_sum += p;
                mean_x += i * dx * p;
            }
            mean_x /= prob_sum;
            
            std::cout << "Крок t = " << step * dt * 1e15 << " fs | Позиція максимуму x_avg = " 
                      << mean_x * 1e9 << " нм | Норма стан = " << prob_sum * dx << "\n";
        }
        
        // Перерахунок хвильової функції на наступному часовому кроці
        std::vector<Complex> psi_next = psi;
        for (size_t i = 1; i < N - 1; ++i) {
            Complex V_term = std::complex<double>(0.0, - (dt / hbar) * V[i]) * psi[i];
            psi_next[i] = psi[i] + alpha * (psi[i+1] - 2.0 * psi[i] + psi[i-1]) + V_term;
        }
        psi = std::move(psi_next);
    }
    
    return 0;
}
