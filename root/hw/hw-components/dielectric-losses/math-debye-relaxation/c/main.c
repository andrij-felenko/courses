#include <stdio.h>
#include <math.h>

#define EPS_0 8.8541878128e-12

typedef struct {
    double eps_s;      // Статична проникність
    double eps_inf;    // Оптична проникність
    double tau;        // Час релаксації (с)
    double c_nom;      // Номінальна ємність (Ф)
    double r_dc;       // Омічний опір металу на DC (Ом)
    double k_skin;     // Коефіцієнт скін-ефекту (Ом/sqrt(Гц))
} DielectricModel;

typedef struct {
    double f;          // Частота (Гц)
    double eps_real;   // Дійсна проникність eps'
    double eps_imag;   // Уявна проникність eps''
    double tan_delta;  // Тангенс кута втрат
    double r_di;       // Діелектричний опір втрат (Ом)
    double r_ohm;      // Омічний опір металу зі скін-ефектом (Ом)
    double esr;        // Сумарний ESR (Ом)
    double q_factor;   // Добротність Q
} CapacitorMetrics;

CapacitorMetrics compute_losses(const DielectricModel *m, double freq_hz) {
    CapacitorMetrics res;
    res.f = freq_hz;

    double omega = 2.0 * M_PI * freq_hz;
    double wt = omega * m->tau;
    double wt_sq = wt * wt;

    // Формули Дебая
    res.eps_real = m->eps_inf + (m->eps_s - m->eps_inf) / (1.0 + wt_sq);
    res.eps_imag = (m->eps_s - m->eps_inf) * wt / (1.0 + wt_sq);
    res.tan_delta = res.eps_imag / res.eps_real;

    // Розрахунок опорів
    res.r_di = res.tan_delta / (omega * m->c_nom);
    res.r_ohm = m->r_dc + m->k_skin * sqrt(freq_hz);
    res.esr = res.r_di + res.r_ohm;
    res.q_factor = 1.0 / res.tan_delta;

    return res;
}

int main(void) {
    DielectricModel x7r = {
        .eps_s = 2200.0,
        .eps_inf = 120.0,
        .tau = 1.5e-8,       // 15 нс (релаксація доменів)
        .c_nom = 100e-9,     // 100 нФ
        .r_dc = 0.012,       // 12 мОм
        .k_skin = 1.2e-6     // скін-ефект у тонких електродах
    };

    double test_freqs[] = {1e2, 1e3, 1e4, 1e5, 1e6, 1e7};
    printf("Частота (Гц) | eps'    | eps''   | tan(delta) | R_di (Ом)  | ESR (Ом)   | Q\n");
    printf("-------------+---------+---------+------------+------------+------------+-------\n");

    for (int i = 0; i < 6; ++i) {
        CapacitorMetrics met = compute_losses(&x7r, test_freqs[i]);
        printf("%12.0f | %7.1f | %7.2f | %10.5f | %10.5f | %10.5f | %7.1f\n",
               met.f, met.eps_real, met.eps_imag, met.tan_delta, met.r_di, met.esr, met.q_factor);
    }
    return 0;
}
