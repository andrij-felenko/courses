/*
 * Hybrid Shield Grounding Impedance & Shielding Effectiveness Calculator
 * Standard: ISO/IEC 9899:1999 (C99)
 *
 * Compilation:
 *   gcc -std=c99 -O3 -Wall -Wextra proj-hybrid-shield-calc.c -lm -o hybrid_calc
 *   clang -std=c99 -O3 -Wall -Wextra proj-hybrid-shield-calc.c -lm -o hybrid_calc
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <stdbool.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define MU_0 (4.0 * M_PI * 1.0e-7)
#define COPPER_SIGMA (5.8e7)

/* Конфігурація фізичних параметрів кабелю */
typedef struct {
    double length_m;            /* Довжина кабелю, метри */
    double r_dc_per_m;          /* Погонний активний опір екрана, Ом/м */
    double braid_diameter_m;    /* Зовнішній діаметр обплетення, метри */
    double wire_diameter_m;     /* Діаметр дротика плетіння, метри */
    double optical_coverage;    /* Оптична щільність переплетення (0.50 - 0.98) */
    double l_ext_per_m;         /* Зовнішня погонна індуктивність контуру, Гн/м */
} CableConfig;

/* Конфігурація вузла гібридного заземлення */
typedef struct {
    double r_bleed_ohm;         /* Опір антистатичного резистора, Ом */
    double c_rf_farad;          /* Ємність високочастотного конденсатора, Ф */
    double esl_henry;           /* Паразитна індуктивність конденсатора ESL, Гн */
    double esr_ohm;             /* Опір втрат конденсатора ESR, Ом */
    double c_gdt_farad;         /* Паразитна ємність газорозрядника GDT, Ф */
    double v_gnd_rms_volts;     /* Діюча різниця потенціалів між землями, В */
    double v_cap_rating_volts;  /* Номінальна робоча напруга конденсатора, В */
} TerminationConfig;

/* Результати розрахунку для однієї частотної точки */
typedef struct {
    double freq_hz;
    double complex z_t_per_m;
    double complex z_hybrid;
    double complex z_loop_total;
    double i_loop_rms_amps;
    double v_noise_cm_volts;
    double shielding_eff_db;
    double v_cap_peak_volts;
    double p_res_watts;
} SweepPointResult;

/* Обчислення глибини скін-шару для міді */
static inline double calc_skin_depth(double freq_hz) {
    if (freq_hz <= 1.0) return 0.066; /* ~66 мм на DC/1 Гц */
    return sqrt(1.0 / (M_PI * freq_hz * MU_0 * COPPER_SIGMA));
}

/* Обчислення поверхневого передавального імпедансу плетеного екрана Z_t(f) */
double complex calc_transfer_impedance(const CableConfig *c, double freq_hz) {
    if (freq_hz <= 0.0) {
        return c->r_dc_per_m + 0.0 * I;
    }

    const double delta = calc_skin_depth(freq_hz);
    const double d = 2.0 * c->wire_diameter_m;
    const double complex gamma = (1.0 + I) / delta;
    const double complex gamma_d = gamma * d;

    /* Дифузійна складова: R_dc * (gamma * d) / sinh(gamma * d) */
    double complex z_diff;
    if (cabs(gamma_d) < 1e-4) {
        z_diff = c->r_dc_per_m + 0.0 * I;
    } else {
        z_diff = c->r_dc_per_m * (gamma_d / csinh(gamma_d));
    }

    /* Індуктивність отворів плетіння: M_h ~ mu_0 / (6*pi) * (1-K)^(3/2) */
    const double k_cov = (c->optical_coverage < 0.99) ? c->optical_coverage : 0.99;
    const double m_h = (MU_0 / (6.0 * M_PI)) * pow(1.0 - k_cov, 1.5) * (d / (c->braid_diameter_m * 0.5));
    const double complex z_hole = I * (2.0 * M_PI * freq_hz * m_h);

    return z_diff + z_hole;
}

/* Обчислення комплексного імпедансу гібридного вузла Z_hybrid(f) */
double complex calc_hybrid_node(const TerminationConfig *t, double freq_hz) {
    if (freq_hz <= 0.0) {
        return t->r_bleed_ohm + 0.0 * I;
    }

    const double omega = 2.0 * M_PI * freq_hz;

    /* Гілка конденсатора C_rf + ESL + ESR */
    const double xc = 1.0 / (omega * t->c_rf_farad);
    const double xl = omega * t->esl_henry;
    const double complex z_cap = t->esr_ohm + I * (xl - xc);

    /* Гілка резистора R_bleed */
    const double complex z_res = t->r_bleed_ohm + 0.0 * I;

    /* Гілка GDT (ємність 0.5-1.5 пФ) */
    const double complex z_gdt = -I / (omega * t->c_gdt_farad);

    /* Паралельне з'єднання трьох гілок: Y_total = 1/Z_c + 1/Z_r + 1/Z_gdt */
    const double complex y_total = (1.0 / z_cap) + (1.0 / z_res) + (1.0 / z_gdt);

    return 1.0 / y_total;
}

/* Розрахунок однієї точки частотного сканування */
SweepPointResult evaluate_frequency_point(const CableConfig *c, const TerminationConfig *t, double freq_hz) {
    SweepPointResult r;
    r.freq_hz = freq_hz;

    r.z_t_per_m = calc_transfer_impedance(c, freq_hz);
    r.z_hybrid = calc_hybrid_node(t, freq_hz);

    /* Повний поздовжній імпеданс зовнішнього контуру екрана */
    const double omega = 2.0 * M_PI * freq_hz;
    const double delta = calc_skin_depth(freq_hz);
    const double r_skin_factor = (delta > 0.0) ? (c->wire_diameter_m / (2.0 * delta)) : 1.0;
    const double r_ac_per_m = c->r_dc_per_m * ((r_skin_factor > 1.0) ? r_skin_factor : 1.0);
    const double complex z_shield_ext = (r_ac_per_m + I * (omega * c->l_ext_per_m)) * c->length_m;

    /* Контактний опір роз'єму Вузла A (360-градусний затискач) */
    const double complex z_contact_a = 0.005 + I * (omega * 0.5e-9);

    r.z_loop_total = z_contact_a + z_shield_ext + r.z_hybrid;

    const double z_loop_mag = cabs(r.z_loop_total);
    r.i_loop_rms_amps = (z_loop_mag > 1e-12) ? (t->v_gnd_rms_volts / z_loop_mag) : 0.0;

    /* Синфазна напруга шуму, наведена на внутрішні жили */
    const double complex v_noise_vec = (r.i_loop_rms_amps + 0.0 * I) * r.z_t_per_m * c->length_m;
    r.v_noise_cm_volts = cabs(v_noise_vec);

    /* Ефективність екранування: SE = 20 * log10(V_gnd / V_noise) */
    if (r.v_noise_cm_volts > 1e-12 && t->v_gnd_rms_volts > 1e-12) {
        r.shielding_eff_db = 20.0 * log10(t->v_gnd_rms_volts / r.v_noise_cm_volts);
    } else {
        r.shielding_eff_db = 120.0;
    }

    /* Напруга та потужність на вузлі для аналізу надійності */
    const double v_hybrid_rms = r.i_loop_rms_amps * cabs(r.z_hybrid);
    r.v_cap_peak_volts = v_hybrid_rms * sqrt(2.0);
    r.p_res_watts = (v_hybrid_rms * v_hybrid_rms) / t->r_bleed_ohm;

    return r;
}

/* Друк інженерного звіту в термінал */
void print_sweep_table(const SweepPointResult *results, size_t count, const TerminationConfig *t) {
    printf("\n====================================================================================================\n");
    printf("        ЧАСТОТНИЙ АНАЛІЗ ГІБРИДНОГО ЗАЗЕМЛЕННЯ ЕКРАНА КАБЕЛЮ (IEC 61000-4-5 / CISPR 32)            \n");
    printf("====================================================================================================\n");
    printf(" Частота [Гц] | |Z_hyb| [Ом] | |Z_loop| [Ом] | I_loop [мкА] | V_noise [мВ] | SE [дБ] | V_cap [В] | Стан \n");
    printf("--------------+--------------+---------------+--------------+--------------+---------+-----------+------\n");

    for (size_t i = 0; i < count; ++i) {
        const SweepPointResult *r = &results[i];
        const char *status = "НОРМА";

        if (r->v_cap_peak_volts > t->v_cap_rating_volts * 0.7) {
            status = "УВАГА!";
        }

        printf(" %12.1f | %12.3f | %13.3f | %12.2f | %12.4f | %7.1f | %9.3f | %s\n",
               r->freq_hz,
               cabs(r->z_hybrid),
               cabs(r->z_loop_total),
               r->i_loop_rms_amps * 1.0e6,
               r->v_noise_cm_volts * 1.0e3,
               r->shielding_eff_db,
               r->v_cap_peak_volts,
               status);
    }
    printf("====================================================================================================\n\n");
}

int main(int argc, char **argv) {
    /* Параметри кабелю за замовчуванням (Belden 9841, кручена пара в екрані) */
    CableConfig cable = {
        .length_m = 50.0,
        .r_dc_per_m = 0.0145,       /* 14.5 мОм/м */
        .braid_diameter_m = 0.0060,  /* 6.0 мм */
        .wire_diameter_m = 0.00016,  /* 0.16 мм */
        .optical_coverage = 0.90,    /* 90% */
        .l_ext_per_m = 0.85e-6       /* 0.85 мкГн/м над шасі */
    };

    /* Параметри вузла гібридного заземлення */
    TerminationConfig term = {
        .r_bleed_ohm = 1.0e6,        /* 1 МОм */
        .c_rf_farad = 10.0e-9,       /* 10 нФ */
        .esl_henry = 1.5e-9,         /* 1.5 нГн (SMD 1812) */
        .esr_ohm = 0.02,             /* 20 мОм */
        .c_gdt_farad = 1.0e-12,      /* 1.0 пФ */
        .v_gnd_rms_volts = 10.0,     /* 10 В 50 Гц */
        .v_cap_rating_volts = 2000.0 /* 2 кВ */
    };

    bool csv_mode = false;
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--csv") == 0) csv_mode = true;
        if (strcmp(argv[i], "--length") == 0 && i + 1 < argc) cable.length_m = atof(argv[++i]);
        if (strcmp(argv[i], "--vgnd") == 0 && i + 1 < argc) term.v_gnd_rms_volts = atof(argv[++i]);
    }

    const double test_freqs[] = {
        10.0, 50.0, 100.0, 1.0e3, 10.0e3, 100.0e3,
        500.0e3, 1.0e6, 5.0e6, 10.0e6, 25.0e6, 50.0e6,
        100.0e6, 250.0e6, 500.0e6, 1000.0e6
    };
    const size_t num_points = sizeof(test_freqs) / sizeof(test_freqs[0]);

    SweepPointResult results[num_points];
    for (size_t i = 0; i < num_points; ++i) {
        results[i] = evaluate_frequency_point(&cable, &term, test_freqs[i]);
    }

    if (csv_mode) {
        printf("Frequency_Hz,Z_hybrid_Ohm,Z_loop_Ohm,I_loop_uA,V_noise_mV,SE_dB,V_cap_V\n");
        for (size_t i = 0; i < num_points; ++i) {
            printf("%.1f,%.4e,%.4e,%.4e,%.4e,%.2f,%.4e\n",
                   results[i].freq_hz,
                   cabs(results[i].z_hybrid),
                   cabs(results[i].z_loop_total),
                   results[i].i_loop_rms_amps * 1.0e6,
                   results[i].v_noise_cm_volts * 1.0e3,
                   results[i].shielding_eff_db,
                   results[i].v_cap_peak_volts);
        }
    } else {
        printf("Конфігурація системи:\n");
        printf("  Довжина кабелю: %.1f м | Погонний опір: %.2f мОм/м | Оптичне покриття: %.0f%%\n",
               cable.length_m, cable.r_dc_per_m * 1000.0, cable.optical_coverage * 100.0);
        printf("  Гібридний вузол: C = %.1f нФ (ESL = %.1f нГн) || R = %.1f МОм || GDT = %.1f пФ\n",
               term.c_rf_farad * 1.0e9, term.esl_henry * 1.0e9, term.r_bleed_ohm / 1.0e6, term.c_gdt_farad * 1.0e12);
        printf("  Різниця потенціалів заземлювачів: %.1f В (RMS)\n", term.v_gnd_rms_volts);

        print_sweep_table(results, num_points, &term);
    }

    return 0;
}
