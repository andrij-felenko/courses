#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double capacitance_f;  /* Номінальна ємність (Ф) */
    double esr_ohm;        /* Еквівалентний послідовний опір (Ом) */
    double esl_h;          /* Еквівалентна індуктивність з монтажем (Гн) */
    int count;             /* Кількість паралельних конденсаторів */
    const char* label;     /* Опис групи */
} DecouplingGroup;

typedef struct {
    double v_dd;           /* Напруга живлення (В) */
    double ripple_ratio;   /* Допустима пульсація (частка, напр. 0.03 = 3%) */
    double i_transient;    /* Стрибок струму споживання (А) */
    double target_z;       /* Розрахований цільовий імпеданс (Ом) */
} PdnSpec;

/* Розрахунок комплексного імпедансу однієї групи конденсаторів */
double complex calc_group_impedance(const DecouplingGroup* g, double freq_hz) {
    if (g->count <= 0 || freq_hz <= 0.0) {
        return CMPLX(1e9, 0.0);
    }
    double w = 2.0 * M_PI * freq_hz;
    double r_eq = g->esr_ohm / (double)g->count;
    double l_eq = g->esl_h / (double)g->count;
    double c_eq = g->capacitance_f * (double)g->count;
    
    double x_l = w * l_eq;
    double x_c = 1.0 / (w * c_eq);
    return CMPLX(r_eq, x_l - x_c);
}

/* Розрахунок сумарного імпедансу мережі PDN */
double complex calc_total_pdn_z(const DecouplingGroup* groups, size_t num_groups,
                                double vrm_r, double vrm_l, double freq_hz) {
    double w = 2.0 * M_PI * freq_hz;
    /* Провідність VRM */
    double complex z_vrm = CMPLX(vrm_r, w * vrm_l);
    double complex y_total = 1.0 / z_vrm;
    
    /* Додавання паралельних провідностей груп конденсаторів */
    for (size_t i = 0; i < num_groups; ++i) {
        double complex z_grp = calc_group_impedance(&groups[i], freq_hz);
        y_total += 1.0 / z_grp;
    }
    return 1.0 / y_total;
}

int main(void) {
    PdnSpec spec = {
        .v_dd = 0.85,
        .ripple_ratio = 0.03,
        .i_transient = 20.0,
        .target_z = (0.85 * 0.03) / 20.0 /* 1.275 мОм */
    };
    
    DecouplingGroup groups[] = {
        { .capacitance_f = 470e-6, .esr_ohm = 0.005, .esl_h = 1.5e-9, .count = 4,  .label = "4x 470uF Bulk Tantalum" },
        { .capacitance_f = 22e-6,  .esr_ohm = 0.006, .esl_h = 0.8e-9, .count = 10, .label = "10x 22uF 0805 MLCC" },
        { .capacitance_f = 1.0e-6, .esr_ohm = 0.010, .esl_h = 0.5e-9, .count = 20, .label = "20x 1.0uF 0402 MLCC" },
        { .capacitance_f = 0.1e-6, .esr_ohm = 0.020, .esl_h = 0.4e-9, .count = 40, .label = "40x 0.1uF 0201 MLCC" }
    };
    size_t num_groups = sizeof(groups) / sizeof(groups[0]);
    
    double vrm_r = 0.0006; /* 0.6 мОм */
    double vrm_l = 2.5e-9;  /* 2.5 нГн */
    
    printf("=== Аналіз профілю імпедансу PDN ===
");
    printf("V_dd = %.2f В, I_step = %.1f А, Допуск = %.1f%%
",
           spec.v_dd, spec.i_transient, spec.ripple_ratio * 100.0);
    printf("Z_target = %.6f Ом (%.3f мОм)

", spec.target_z, spec.target_z * 1000.0);
    
    double f_start = 1e3;   /* 1 кГц */
    double f_stop  = 1e8;   /* 100 МГц */
    int points_per_decade = 5;
    
    double max_z = 0.0;
    double max_z_freq = 0.0;
    bool target_exceeded = false;
    
    for (double f = f_start; f <= f_stop; f *= pow(10.0, 1.0 / points_per_decade)) {
        double complex z = calc_total_pdn_z(groups, num_groups, vrm_r, vrm_l, f);
        double mag_z = cabs(z);
        
        if (mag_z > max_z) {
            max_z = mag_z;
            max_z_freq = f;
        }
        if (mag_z > spec.target_z) {
            target_exceeded = true;
        }
        
        printf("f = %10.1f Гц | |Z| = %8.4f мОм | Фаза = %6.1f град %s
",
               f, mag_z * 1000.0, carg(z) * 180.0 / M_PI,
               (mag_z > spec.target_z) ? " [ПЕРЕВИЩЕННЯ Z_TARGET!]" : "");
    }
    
    printf("
Підсумок аналізу:
");
    printf("Максимальний імпеданс: %.3f мОм на частоті %.2f МГц
",
           max_z * 1000.0, max_z_freq / 1e6);
    if (target_exceeded) {
        printf("СТАТУС: ПОМИЛКА — Профіль імпедансу перевищує Z_target! Потрібне демпфування.
");
    } else {
        printf("СТАТУС: УСПІХ — Профіль імпедансу повністю задовольняє Z_target.
");
    }
    return 0;
}
