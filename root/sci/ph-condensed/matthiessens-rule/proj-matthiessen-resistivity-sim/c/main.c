#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Структура фізичних параметрів металу чи сплаву */
typedef struct {
    const char *name;
    double theta_D;      /* Температура Дебая, К */
    double A_phonon;     /* Амплітудний коефіцієнт фононного опору, мкОм·см */
    double rho_0;        /* Залишковий опір на домішках, мкОм·см */
} MetalParams;

/* Підінтегральна функція Блоха-Ґрюнайзена f(z) = z^5 / ((e^z - 1)*(1 - e^-z)) */
static double bloch_gruneisen_kernel(double z) {
    if (z < 1e-4) {
        /* Тейлорівський граничний перехід при z -> 0: z^5 / (z * z) = z^3 */
        return z * z * z;
    }
    double ez = exp(z);
    return (z * z * z * z * z) / ((ez - 1.0) * (1.0 - 1.0 / ez));
}

/* Обчислення інтеграла методом Сімпсона з N кроками */
static double integrate_bloch_gruneisen(double x_max, int steps) {
    if (x_max <= 0.0) return 0.0;
    if (steps % 2 != 0) steps++;
    
    double h = x_max / steps;
    double sum = bloch_gruneisen_kernel(0.0) + bloch_gruneisen_kernel(x_max);
    
    for (int i = 1; i < steps; i++) {
        double z = i * h;
        double weight = (i % 2 == 1) ? 4.0 : 2.0;
        sum += weight * bloch_gruneisen_kernel(z);
    }
    return (h / 3.0) * sum;
}

/* Обчислення фононного питомого опору за формулою Блоха-Ґрюнайзена */
double calc_phonon_resistivity(double T_kelvin, double theta_D, double A_coeff) {
    if (T_kelvin <= 1e-3) return 0.0;
    double x_max = theta_D / T_kelvin;
    double ratio = T_kelvin / theta_D;
    double integral = integrate_bloch_gruneisen(x_max, 500);
    return A_coeff * pow(ratio, 5.0) * integral;
}

/* Розрахунок RRR (Residual Resistivity Ratio) = ρ(293.15 K) / ρ(4.2 K) */
double calc_rrr(const MetalParams *m) {
    double rho_293 = m->rho_0 + calc_phonon_resistivity(293.15, m->theta_D, m->A_phonon);
    double rho_4_2 = m->rho_0 + calc_phonon_resistivity(4.2, m->theta_D, m->A_phonon);
    return rho_293 / rho_4_2;
}

/* Обчислення двозонного опору та відхилення від правила Матіссена (DMR) */
void calc_two_band_dmr(double T, double rho_s0, double rho_d0, 
                        double A_s, double A_d, double theta_D,
                        double *out_rho_tot, double *out_dmr) {
    double rho_sph = calc_phonon_resistivity(T, theta_D, A_s);
    double rho_dph = calc_phonon_resistivity(T, theta_D, A_d);
    
    double rho_s = rho_s0 + rho_sph;
    double rho_d = rho_d0 + rho_dph;
    
    /* Паралельне додавання провідностей: 1 / ρ_tot = 1/ρ_s + 1/ρ_d */
    double rho_tot = (rho_s * rho_d) / (rho_s + rho_d);
    
    /* Проста адитивна сума Матіссена для двох зон */
    double rho_0_tot = (rho_s0 * rho_d0) / (rho_s0 + rho_d0);
    double rho_ph_tot = (rho_sph * rho_dph) / (rho_sph + rho_dph);
    double rho_matthiessen = rho_0_tot + rho_ph_tot;
    
    *out_rho_tot = rho_tot;
    *out_dmr = rho_tot - rho_matthiessen;
}

int main(void) {
    MetalParams pure_cu = {"Чиста мідь (OFHC 5N)", 343.0, 15.2, 0.0016};
    MetalParams alloy_cu = {"Сплав Cu-0.1%Ni", 343.0, 15.2, 0.1250};

    printf("=== МОДЕЛЮВАННЯ ПРАВИЛА МАТІССЕНА ТА РЕСУРСУ RRR ===\n\n");
    printf("Метал: %s | Theta_D = %.1f K | rho_0 = %.4f мкОм·см\n",
           pure_cu.name, pure_cu.theta_D, pure_cu.rho_0);
    printf("Сплав: %s | Theta_D = %.1f K | rho_0 = %.4f мкОм·см\n\n",
           alloy_cu.name, alloy_cu.theta_D, alloy_cu.rho_0);

    printf("%-8s | %-18s | %-18s | %-16s\n", "T (K)", "rho_pure (мкОм·см)", "rho_alloy (мкОм·см)", "Delta_rho");
    printf("-------------------------------------------------------------------\n");

    double temps[] = {1.0, 4.2, 10.0, 20.0, 50.0, 100.0, 200.0, 293.15, 500.0};
    int num_t = sizeof(temps) / sizeof(temps[0]);

    for (int i = 0; i < num_t; i++) {
        double T = temps[i];
        double rho_ph = calc_phonon_resistivity(T, pure_cu.theta_D, pure_cu.A_phonon);
        double rho_p = pure_cu.rho_0 + rho_ph;
        double rho_a = alloy_cu.rho_0 + rho_ph;
        double diff = rho_a - rho_p;

        printf("%-8.1f | %-18.6f | %-18.6f | %-16.6f\n", T, rho_p, rho_a, diff);
    }

    printf("-------------------------------------------------------------------\n");
    printf("RRR чистої міді: %.1f\n", calc_rrr(&pure_cu));
    printf("RRR сплаву Cu-Ni: %.2f\n\n", calc_rrr(&alloy_cu));

    printf("=== ОБЧИСЛЕННЯ ДВОЗОННОГО ВІДХИЛЕННЯ (DMR) ДЛЯ ПЛАТИНИ (Pt) ===\n");
    printf("%-8s | %-18s | %-16s\n", "T (K)", "rho_total (мкОм·см)", "DMR Delta_rho");
    printf("----------------------------------------------------\n");
    
    for (int i = 0; i < num_t; i++) {
        double T = temps[i];
        double rho_tot, dmr;
        /* Параметри платини: s-зона (рухлива) та d-зона (важка) */
        calc_two_band_dmr(T, 0.05, 0.80, 12.0, 45.0, 240.0, &rho_tot, &dmr);
        printf("%-8.1f | %-18.6f | %-16.6f\n", T, rho_tot, dmr);
    }

    return 0;
}
