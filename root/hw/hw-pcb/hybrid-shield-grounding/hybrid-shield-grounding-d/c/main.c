/*
 * Модуль розрахунку імпедансу гібридного заземлення екрана (C99).
 * Обчислює частотну характеристику паралельного RC-вузла з урахуванням
 * паразитних параметрів ESL та ESR.
 */

#include <stdio.h>
#include <math.h>
#include <complex.h>
#include <stdbool.h>

typedef struct {
    double r_bleed_ohm;     /* Опір антистатичного резистора, Ом */
    double c_rf_farad;       /* Ємність ВЧ конденсатора, Ф */
    double esl_henry;        /* Еквівалентна послідовна індуктивність ESL, Гн */
    double esr_ohm;          /* Еквівалентний послідовний опір ESR, Ом */
    double v_gnd_rms_volts;  /* Різниця потенціалів між заземлювачами, В */
} HybridGroundConfig;

typedef struct {
    double freq_hz;
    double complex z_hybrid_ohm;
    double i_loop_rms_amps;
    double attenuation_db;
} GroundCalcResult;

GroundCalcResult calculate_hybrid_point(const HybridGroundConfig *cfg, double freq_hz) {
    GroundCalcResult res;
    res.freq_hz = freq_hz;

    if (freq_hz <= 0.0) {
        res.z_hybrid_ohm = cfg->r_bleed_ohm;
        res.i_loop_rms_amps = cfg->v_gnd_rms_volts / cfg->r_bleed_ohm;
        res.attenuation_db = 0.0;
        return res;
    }

    const double omega = 2.0 * M_PI * freq_hz;

    /* Гілка конденсатора: Z_c = ESR + j*(omega*ESL - 1/(omega*C)) */
    const double xc = 1.0 / (omega * cfg->c_rf_farad);
    const double xl = omega * cfg->esl_henry;
    const double complex z_cap_branch = cfg->esr_ohm + I * (xl - xc);

    /* Гілка резистора: Z_r = R_bleed */
    const double complex z_res_branch = cfg->r_bleed_ohm;

    /* Паралельне з'єднання: Z_total = (Z_c * Z_r) / (Z_c + Z_r) */
    res.z_hybrid_ohm = (z_cap_branch * z_res_branch) / (z_cap_branch + z_res_branch);

    const double z_mag = cabs(res.z_hybrid_ohm);
    res.i_loop_rms_amps = (z_mag > 1e-12) ? (cfg->v_gnd_rms_volts / z_mag) : 0.0;

    /* Оцінка послаблення завади відносно незаземленого екрана */
    res.attenuation_db = -20.0 * log10(z_mag / (z_mag + 50.0));

    return res;
}

int main(void) {
    HybridGroundConfig cfg = {
        .r_bleed_ohm = 1.0e6,     /* 1 МОм */
        .c_rf_farad = 10.0e-9,    /* 10 нФ */
        .esl_henry = 1.5e-9,      /* 1.5 нГн */
        .esr_ohm = 0.02,          /* 20 мОм */
        .v_gnd_rms_volts = 10.0   /* 10 В 50 Гц */
    };

    const double test_freqs[] = { 50.0, 1.0e3, 100.0e3, 1.0e6, 10.0e6, 50.0e6, 100.0e6 };
    const size_t n_freqs = sizeof(test_freqs) / sizeof(test_freqs[0]);

    printf("Частота [Гц]    |Z_hybrid| [Ом]    I_loop [мкА]    Послаблення [дБ]\n");
    printf("------------------------------------------------------------------\n");

    for (size_t i = 0; i < n_freqs; ++i) {
        GroundCalcResult r = calculate_hybrid_point(&cfg, test_freqs[i]);
        printf("%12.1f    %14.4f    %12.3f    %16.2f\n",
               r.freq_hz, cabs(r.z_hybrid_ohm), r.i_loop_rms_amps * 1.0e6, r.attenuation_db);
    }

    return 0;
}
