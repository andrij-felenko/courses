#include <math.h>

// Коефіцієнти IEC 60751 для PT100 (R0 = 100.0 Ом)
#define RTD_R0 100.0
#define RTD_A  3.9083e-3
#define RTD_B  -5.775e-7
#define RTD_C  -4.183e-12

/**
 * Обчислення температури за опором RTD (IEC 60751)
 * @param r_ohm Виміряний опір у Омах
 * @return Температура у градусах Цельсія
 */
double rtd_convert_r_to_t(double r_ohm) {
    // 1. Квадратне розв'язання для t >= 0 °C (або як початкове наближення)
    double Z1 = -RTD_A;
    double Z2 = RTD_A * RTD_A - (4.0 * RTD_B * (1.0 - r_ohm / RTD_R0));
    double t = (Z1 + sqrt(Z2)) / (2.0 * RTD_B);

    // Якщо опір менше R0 (t < 0 °C), уточнюємо методом Ньютона — Рафсона
    if (r_ohm < RTD_R0) {
        for (int i = 0; i < 2; i++) { // 2 ітерації достатньо для точності < 0.001 °C
            double t2 = t * t;
            double t3 = t2 * t;
            double t4 = t3 * t;
            
            // f(t) = R(t) - R_measured
            double f = RTD_R0 * (1.0 + RTD_A * t + RTD_B * t2 + RTD_C * (t - 100.0) * t3) - r_ohm;
            
            // f'(t) = dR/dt = R0 * (A + 2*B*t - 300*C*t^2 + 4*C*t^3)
            double f_prime = RTD_R0 * (RTD_A + 2.0 * RTD_B * t - 300.0 * RTD_C * t2 + 4.0 * RTD_C * t3);
            
            t = t - f / f_prime;
        }
    }

    return t;
}
