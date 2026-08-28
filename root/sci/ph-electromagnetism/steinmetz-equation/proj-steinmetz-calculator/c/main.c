/* Steinmetz Core Loss Calculator (C implementation) */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double k;     /* Коефіцієнт Штейнмеця (для f в Гц, B у Тл) */
    double alpha; /* Експонента по частоті */
    double beta;  /* Експонента по індукції */
} SteinmetzParams;

/* Обчислення Бета-функції B(x, y) = Gamma(x)*Gamma(y)/Gamma(x+y) */
static double beta_func(double x, double y) {
    return (tgamma(x) * tgamma(y)) / tgamma(x + y);
}

/* Обчислення коефіцієнта k_i для iSE */
double calculate_k_i(const SteinmetzParams *p) {
    double term1 = pow(2.0 * M_PI, p->alpha - 1.0);
    double term2 = pow(2.0, p->beta - p->alpha + 1.0);
    double beta_val = beta_func((p->alpha + 1.0) / 2.0, 0.5);
    
    return p->k / (term1 * term2 * beta_val);
}

/* Розрахунок втрат OSE для синусоїди: P_v = k * f^alpha * B_m^beta */
double calculate_ose_loss(const SteinmetzParams *p, double freq_hz, double b_peak_tesla) {
    return p->k * pow(freq_hz, p->alpha) * pow(b_peak_tesla, p->beta);
}

/* Розрахунок втрат iSE для довільного часового сигналу B(t) */
double calculate_ise_loss(const SteinmetzParams *p, const double *b_samples, 
                           size_t num_samples, double period_sec) {
    if (num_samples < 2 || period_sec <= 0.0) return 0.0;
    
    double dt = period_sec / (double)(num_samples - 1);
    double b_min = b_samples[0];
    double b_max = b_samples[0];
    
    /* Знаходимо розмах індукції ΔB */
    for (size_t i = 1; i < num_samples; ++i) {
        if (b_samples[i] < b_min) b_min = b_samples[i];
        if (b_samples[i] > b_max) b_max = b_samples[i];
    }
    double delta_b = b_max - b_min;
    if (delta_b <= 0.0) return 0.0;
    
    double k_i = calculate_k_i(p);
    double integral_sum = 0.0;
    
    /* Числове інтегрування |dB/dt|^alpha */
    for (size_t i = 0; i < num_samples - 1; ++i) {
        double db_dt = (b_samples[i + 1] - b_samples[i]) / dt;
        integral_sum += pow(fabs(db_dt), p->alpha) * dt;
    }
    
    double avg_integral = integral_sum / period_sec;
    double p_v = k_i * avg_integral * pow(delta_b, p->beta - p->alpha);
    
    return p_v;
}

int main(void) {
    /* Параметри матеріалу N87 (Epcos): k=16.9, alpha=1.25, beta=2.55 */
    SteinmetzParams n87 = {16.9, 1.25, 2.55};
    double freq = 100000.0;   /* 100 кГц */
    double b_pk = 0.1;        /* 100 мТл */
    
    double ose_p_v = calculate_ose_loss(&n87, freq, b_pk);
    printf("OSE Power Loss Density: %.2f W/m^3 (%.2f mW/cm^3)\n", 
           ose_p_v, ose_p_v / 1000.0);
           
    return 0;
}
