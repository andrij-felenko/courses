#include <math.h>
#include <stdbool.h>

// Константи стандарту IEC 60751 для датчика PT100
#define RTD_R0 100.0f
#define RTD_A  3.9083e-3f
#define RTD_B  -5.775e-7f
#define RTD_C  -4.183e-12f

float rtd_subzero_newton_calc(float r_meas) {
    // 1. Початкове наближення t0 з аналітичного квадратичного розв'язку
    float discr = RTD_A * RTD_A - 4.0f * RTD_B * (1.0f - r_meas / RTD_R0);
    if (discr < 0.0f) {
        return -999.0f; // Помилка: недопустимий опір
    }
    
    float t = (-RTD_A + sqrtf(discr)) / (2.0f * RTD_B);
    
    // Для додатних температур квадратичний розв'язок точний
    if (t >= 0.0f) {
        return t;
    }
    
    // 2. Ітерації Ньютона — Рафсона для від'ємного діапазону (достатньо 2-3 кроків)
    for (int i = 0; i < 3; i++) {
        float t2 = t * t;
        float t3 = t2 * t;
        float t4 = t3 * t;
        
        float f_val = RTD_R0 * (1.0f + RTD_A * t + RTD_B * t2 - 100.0f * RTD_C * t3 + RTD_C * t4) - r_meas;
        float f_prime = RTD_R0 * (RTD_A + 2.0f * RTD_B * t - 300.0f * RTD_C * t2 + 4.0f * RTD_C * t3);
        
        t -= f_val / f_prime;
    }
    
    return t;
}
