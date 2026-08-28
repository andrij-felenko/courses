#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <algorithm>

// Потенціал ангармонічного осцилятора: V(z) = 0.5*z^2 + 0.1*z^4
double potential(double z) {
    return 0.5 * z * z + 0.1 * std::pow(z, 4);
}

// Послідовне інтегрування Нумерова для заданого E
double numerov_integrate(double E, double z_min, double z_max, int N) {
    double h = (z_max - z_min) / N;
    double h2 = h * h;
    
    auto g = [E](double z) { return 2.0 * (E - potential(z)); };
    
    double psi_prev = 0.0;           // ψ(z_min) = 0
    double psi_curr = 1e-5;          // Мала початкова амплітуда
    
    for (int i = 1; i < N; ++i) {
        double z_prev = z_min + (i - 1) * h;
        double z_curr = z_min + i * h;
        double z_next = z_min + (i + 1) * h;
        
        double g_prev = g(z_prev);
        double g_curr = g(z_curr);
        double g_next = g(z_next);
        
        double term_curr = 2.0 * (1.0 - (5.0 * h2 / 12.0) * g_curr) * psi_curr;
        double term_prev = (1.0 + (h2 / 12.0) * g_prev) * psi_prev;
        double term_next_denom = 1.0 + (h2 / 12.0) * g_next;
        
        double psi_next = (term_curr - term_prev) / term_next_denom;
        
        psi_prev = psi_curr;
        psi_curr = psi_next;
    }
    return psi_curr; // Значення незшивки на правій межі
}

// Знаходження власного значення енергії методом бісекції
double find_energy_level(double E_low, double E_high, double z_min, double z_max, int N, double tol = 1e-7) {
    while ((E_high - E_low) > tol) {
        double E_mid = 0.5 * (E_low + E_high);
        double f_low = numerov_integrate(E_low, z_min, z_max, N);
        double f_mid = numerov_integrate(E_mid, z_min, z_max, N);
        
        if (f_low * f_mid <= 0.0) {
            E_high = E_mid;
        } else {
            E_low = E_mid;
        }
    }
    return 0.5 * (E_low + E_high);
}

int main() {
    std::cout << std::fixed << std::setprecision(6);
    std::cout << "=== Рівні енергії ангармонічного осцилятора (C++ Shooting Method) ===\n";
    
    double z_min = -6.0, z_max = 6.0;
    int N = 2000;
    
    // Пошукові інтервали для перших чотирьох рівнів
    std::vector<std::pair<double, double>> intervals = {
        {0.4, 0.7},   // n = 0
        {1.2, 1.6},   // n = 1
        {2.2, 2.7},   // n = 2
        {3.4, 4.0}    // n = 3
    };
    
    for (size_t n = 0; n < intervals.size(); ++n) {
        double E_n = find_energy_level(intervals[n].first, intervals[n].second, z_min, z_max, N);
        std::cout << "Рівень n=" << n << ": E_" << n << " = " << E_n << "\n";
    }
    
    return 0;
}
