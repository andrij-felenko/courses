#include <stdio.h>
#include <math.h>
#include <stdbool.h>

// Чисельне розв'язання рівняння Вейсса методом простої ітерації для C
double solve_weiss_m(double T, double Tc, double tol, int max_iter) {
    if (T >= Tc) {
        return 0.0;
    }
    
    double m_curr = 0.99;
    for (int i = 0; i < max_iter; i++) {
        double m_next = tanh(m_curr * Tc / T);
        if (fabs(m_next - m_curr) < tol) {
            return m_next;
        }
        m_curr = m_next;
    }
    return m_curr;
}

// Лінійна регресія 1/chi = a*T + b для обчислення C та Tc
bool fit_curie_weiss_c(const double* T, const double* chi, int n, double* out_C, double* out_Tc) {
    if (n < 2) return false;
    
    double sum_x = 0.0, sum_y = 0.0, sum_xx = 0.0, sum_xy = 0.0;
    for (int i = 0; i < n; i++) {
        double x = T[i];
        double y = 1.0 / chi[i];
        sum_x += x;
        sum_y += y;
        sum_xx += x * x;
        sum_xy += x * y;
    }
    
    double denom = n * sum_xx - sum_x * sum_x;
    if (fabs(denom) < 1e-12) return false;
    
    double a = (n * sum_xy - sum_x * sum_y) / denom;
    double b = (sum_y - a * sum_x) / (double)n;
    
    if (fabs(a) < 1e-12) return false;
    
    *out_C = 1.0 / a;
    *out_Tc = -b / a;
    return true;
}
