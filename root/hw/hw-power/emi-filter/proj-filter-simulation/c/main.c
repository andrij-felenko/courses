#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#define PI 3.14159265358979323846

// Модель LISN 50 мкГн / 50 Ом
typedef struct {
    double l_choke;
    double r_iso;
    double c_coup;
    double r_meas;
} LisnModel;

double complex lisn_impedance(const LisnModel* lisn, double f) {
    double w = 2.0 * PI * f;
    double complex s = I * w;
    double complex z_b1 = s * lisn->l_choke + lisn->r_iso;
    double complex z_b2 = lisn->r_meas + 1.0 / (s * lisn->c_coup);
    return (z_b1 * z_b2) / (z_b1 + z_b2);
}

typedef struct {
    double c;
    double esr;
    double esl;
} RealCapacitor;

double complex cap_impedance(const RealCapacitor* cap, double f) {
    double w = 2.0 * PI * f;
    double complex s = I * w;
    return cap->esr + s * cap->esl + 1.0 / (s * cap->c);
}

typedef struct {
    double l;
    double dcr;
    double epc;
} RealInductor;

double complex ind_impedance(const RealInductor* ind, double f) {
    double w = 2.0 * PI * f;
    double complex s = I * w;
    double complex z_lr = s * ind->l + ind->dcr;
    if (ind->epc <= 0.0) return z_lr;
    double complex y_epc = s * ind->epc;
    return z_lr / (1.0 + z_lr * y_epc);
}

typedef struct {
    RealCapacitor cx1;
    RealCapacitor cx2;
    RealCapacitor cy;
    RealInductor  l_cm;
    RealInductor  l_leak;
    double r_damp;
    double c_damp;
    LisnModel lisn;
} EmiFilter;

double calculate_il_dm(const EmiFilter* filter, double f, double r_load) {
    double complex z_lisn_dm = 2.0 * lisn_impedance(&filter->lisn, f);
    double complex z_cx1 = cap_impedance(&filter->cx1, f);
    double complex z_cx2 = cap_impedance(&filter->cx2, f);
    double complex z_leak = 2.0 * ind_impedance(&filter->l_leak, f);

    double w = 2.0 * PI * f;
    double complex z_damp = filter->r_damp + 1.0 / (I * w * filter->c_damp);

    double complex v_unfiltered = r_load / (z_lisn_dm + r_load);

    double complex y_in = 1.0 / z_lisn_dm + 1.0 / z_cx1 + 1.0 / z_leak;
    double complex y_out = 1.0 / z_leak + 1.0 / z_cx2 + 1.0 / z_damp + 1.0 / r_load;
    double complex y_m = -1.0 / z_leak;

    double complex det = y_in * y_out - y_m * y_m;
    double complex v_filtered = (1.0 / z_lisn_dm) * (-y_m) / det;

    double ratio = cabs(v_unfiltered / v_filtered);
    if (ratio < 1.0e-6) ratio = 1.0e-6;
    return 20.0 * log10(ratio);
}

double calculate_il_cm(const EmiFilter* filter, double f, double r_cm_source) {
    double complex z_lisn_cm = lisn_impedance(&filter->lisn, f) / 2.0;
    double complex z_cm_choke = ind_impedance(&filter->l_cm, f);

    RealCapacitor cy_total = filter->cy;
    cy_total.c *= 2.0;
    cy_total.esr /= 2.0;
    cy_total.esl /= 2.0;
    double complex z_cy_pair = cap_impedance(&cy_total, f);

    double complex v_unfiltered = z_lisn_cm / (r_cm_source + z_lisn_cm);
    double complex z_total_shunt = z_cy_pair;
    double complex z_ser = z_cm_choke;

    double complex v_filtered = (v_unfiltered * z_total_shunt) / 
                                (z_ser + z_total_shunt + z_lisn_cm);

    double ratio = cabs(v_unfiltered / v_filtered);
    if (ratio < 1.0e-6) ratio = 1.0e-6;
    return 20.0 * log10(ratio);
}

int main(void) {
    EmiFilter filter = {
        .cx1 = {.c = 0.47e-6, .esr = 0.015, .esl = 8.0e-9},
        .cx2 = {.c = 0.22e-6, .esr = 0.020, .esl = 6.0e-9},
        .cy  = {.c = 3.3e-9,  .esr = 0.050, .esl = 3.5e-9},
        .l_cm = {.l = 4.7e-3, .dcr = 0.040, .epc = 15.0e-12},
        .l_leak = {.l = 25.0e-6, .dcr = 0.020, .epc = 3.0e-12},
        .r_damp = 1.0,
        .c_damp = 2.2e-6,
        .lisn = {.l_choke = 50.0e-6, .r_iso = 5.0, .c_coup = 0.1e-6, .r_meas = 50.0}
    };

    printf("========================================================\n");
    printf(" АЧХ затухання вхідного ЕМС-фільтра (Insertion Loss)\n");
    printf("========================================================\n");
    printf("%10s %16s %16s %14s\n", "Частота", "IL_DM (дБ)", "IL_CM (дБ)", "Статус");
    printf("--------------------------------------------------------\n");

    const double freqs[] = {
        10.0e3, 50.0e3, 100.0e3, 150.0e3, 300.0e3, 500.0e3,
        1.0e6, 2.0e6, 5.0e6, 10.0e6, 20.0e6, 30.0e6
    };
    const int num_freqs = sizeof(freqs) / sizeof(freqs[0]);

    for (int i = 0; i < num_freqs; i++) {
        double f = freqs[i];
        double il_dm = calculate_il_dm(&filter, f, 50.0);
        double il_cm = calculate_il_cm(&filter, f, 25.0);

        const char* status = (il_dm >= 30.0 && il_cm >= 40.0) ? "PASS (OK)" : "MARGINAL";
        if (f < 150.0e3) status = "INFO";

        printf("%8.1f кГц %15.2f %15.2f %14s\n", f / 1.0e3, il_dm, il_cm, status);
    }
    printf("========================================================\n");

    return 0;
}
