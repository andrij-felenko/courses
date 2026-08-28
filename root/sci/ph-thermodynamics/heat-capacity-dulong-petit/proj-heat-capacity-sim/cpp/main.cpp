#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <functional>

// Універсальна газова стала R (Дж / (моль·К))
constexpr double R_GAS = 8.314462618;

// Граничне значення закону Дюлонга — Пті (3R)
constexpr double DULONG_PETIT_LIMIT = 3.0 * R_GAS;

// Класична теплоємність за Дюлонгом — Пті (константа 3R)
double heat_capacity_dulong_petit() {
    return DULONG_PETIT_LIMIT;
}

// Модель Ейнштейна: C_v(T/Theta_E)
double heat_capacity_einstein(double t_rel) {
    if (t_rel <= 0.0) return 0.0;
    double x = 1.0 / t_rel;
    if (x > 80.0) return 0.0; // Експоненціальне виморожування
    
    double exp_x = std::exp(x);
    double factor = (x * x * exp_x) / ((exp_x - 1.0) * (exp_x - 1.0));
    return DULONG_PETIT_LIMIT * factor;
}

// Підінтегральна функція моделі Дебая: f(x) = (x^4 * e^x) / (e^x - 1)^2
double debye_integrand(double x) {
    if (x <= 1e-7) return 0.0; // Границя при x -> 0
    if (x > 80.0) return 0.0;  // Запобігання overflow
    
    double exp_x = std::exp(x);
    return (std::pow(x, 4) * exp_x) / ((exp_x - 1.0) * (exp_x - 1.0));
}

// Чисельне інтегрування методом Сімпсона
double simpson_integrate(const std::function<double(double)>& func, double a, double b, int n_steps) {
    if (n_steps % 2 != 0) n_steps++; // Кількість кроків має бути парною
    double h = (b - a) / n_steps;
    double sum = func(a) + func(b);

    for (int i = 1; i < n_steps; i += 2) {
        sum += 4.0 * func(a + i * h);
    }
    for (int i = 2; i < n_steps - 1; i += 2) {
        sum += 2.0 * func(a + i * h);
    }
    return (h / 3.0) * sum;
}

// Модель Дебая: C_v(T/Theta_D)
double heat_capacity_debye(double t_rel) {
    if (t_rel <= 0.0) return 0.0;
    
    // Асимптотика закону T^3 при дуже низьких T (t_rel < 0.08)
    if (t_rel < 0.08) {
        constexpr double pi_val = 3.14159265358979323846;
        double factor = (12.0 * std::pow(pi_val, 4) / 5.0) * std::pow(t_rel, 3);
        return R_GAS * factor;
    }

    double x_upper = 1.0 / t_rel;
    int steps = 200;
    double integral_val = simpson_integrate(debye_integrand, 0.0, x_upper, steps);
    
    double factor = 3.0 * std::pow(t_rel, 3) * integral_val;
    return DULONG_PETIT_LIMIT * factor;
}

int main() {
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "========================================================================\n";
    std::cout << " T / Theta | Dulong-Petit (J/mol/K) | Einstein (J/mol/K) | Debye (J/mol/K)\n";
    std::cout << "========================================================================\n";

    std::vector<double> temps = {0.02, 0.05, 0.10, 0.20, 0.30, 0.50, 0.70, 1.00, 1.50};

    for (double t_rel : temps) {
        double cv_dp = heat_capacity_dulong_petit();
        double cv_e  = heat_capacity_einstein(t_rel);
        double cv_d  = heat_capacity_debye(t_rel);

        std::cout << "   " << std::setw(5) << t_rel << "   |       "
                  << std::setw(7) << cv_dp << "          |      "
                  << std::setw(7) << cv_e  << "       |    "
                  << std::setw(7) << cv_d  << "\n";
    }
    std::cout << "========================================================================\n";
    return 0;
}
