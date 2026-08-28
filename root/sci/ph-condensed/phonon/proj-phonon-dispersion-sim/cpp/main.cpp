#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <string>

// Фізичні константи в системі СІ
constexpr double PI = 3.14159265358979323846;
constexpr double AMU = 1.660539e-27;  // Атомна одиниця маси (кг)
constexpr double R_GAS = 8.31446;     // Універсальна газова стала Дж/(моль·К)

// Підінтегральна функція f(x) = x^4 * e^x / (e^x - 1)^2
double debyeIntegrand(double x) {
    if (x < 1e-5) return x * x;
    if (x > 80.0) return 0.0;
    double exp_x = std::exp(x);
    return (x * x * x * x) * exp_x / ((exp_x - 1.0) * (exp_x - 1.0));
}

// Чисельне інтегрування методом трапецій для C_v(T) / R
double debyeHeatCapacity(double tRatio, int numSteps = 2000) {
    if (tRatio <= 0.0) return 0.0;
    
    // Аналітична асимптотика куба Дебая при дуже низьких T
    if (tRatio < 0.01) {
        return (12.0 * std::pow(PI, 4.0) / 5.0) * std::pow(tRatio, 3.0);
    }
    
    double xMax = 1.0 / tRatio;
    double dx = xMax / numSteps;
    
    double integralSum = 0.5 * (debyeIntegrand(0.0) + debyeIntegrand(xMax));
    for (int i = 1; i < numSteps; ++i) {
        double x = i * dx;
        integralSum += debyeIntegrand(x);
    }
    double integralVal = integralSum * dx;
    return 9.0 * std::pow(tRatio, 3.0) * integralVal;
}

int main() {
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=========================================================\n";
    std::cout << "   C++ РЕАЛІЗАЦІЯ РОЗРАХУНКУ ТЕПЛОЄМНОСТІ ДЕБАЯ C_v(T)\n";
    std::cout << "=========================================================\n\n";
    
    std::cout << "  T/Theta_D  |  Cv / (3R)  |  Cv Дж/(моль·К)  |  Режим\n";
    std::cout << "---------------------------------------------------------\n";
    
    std::vector<double> temps = {0.005, 0.01, 0.05, 0.10, 0.20, 0.50, 1.00, 2.00, 5.00};
    for (double tr : temps) {
        double cv_r = debyeHeatCapacity(tr);
        double cv_norm = cv_r / 3.0;
        double cv_abs = cv_r * R_GAS;
        
        std::string regime;
        if (tr <= 0.05) regime = "T^3 закон Дебая";
        else if (tr >= 2.0) regime = "Границя Дюлонга-Пті";
        else regime = "Перехідна квантова область";
        
        std::cout << "    " << std::setw(5) << tr << "    |   " 
                  << std::setw(6) << cv_norm << "   |     " 
                  << std::setw(7) << cv_abs << "     |  " << regime << "\n";
    }
    
    return 0;
}
