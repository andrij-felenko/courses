#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double amplitude;
    double phase_rad;
    double frequency_hz;
} MagnonWave;

typedef struct {
    double input_phase_a;
    double input_phase_b;
    double output_intensity;
    int logic_bit_xor;
    int logic_bit_and;
} MagnonicGateResult;

typedef struct {
    double alpha_r;       /* Параметр Рашби (еВ·м) */
    double channel_length;/* Довжина каналу (м) */
    double m_eff;         /* Ефективна маса електрона (кг) */
} DattaDasParams;

/* Фізичні константи */
static const double HBAR = 1.054571817e-34; /* Дж·с */
static const double ME = 9.1093837015e-31;  /* кг */
static const double EV_TO_JOULE = 1.602176634e-19;

/* Обчислення інтерференції двох магнонних хвиль */
MagnonicGateResult simulate_magnonic_gate(MagnonWave w1, MagnonWave w2, double threshold) {
    MagnonicGateResult result;
    result.input_phase_a = w1.phase_rad;
    result.input_phase_b = w2.phase_rad;

    double delta_phi = w1.phase_rad - w2.phase_rad;
    double i1 = w1.amplitude * w1.amplitude;
    double i2 = w2.amplitude * w2.amplitude;

    /* Рівняння хвильової інтерференції: I = I1 + I2 + 2*sqrt(I1*I2)*cos(Delta_phi) */
    result.output_intensity = i1 + i2 + 2.0 * sqrt(i1 * i2) * cos(delta_phi);

    /* Детектування логічних станів */
    result.logic_bit_xor = (fabs(delta_phi) > 0.5 * M_PI) ? 1 : 0;
    result.logic_bit_and = (result.output_intensity >= threshold) ? 1 : 0;

    return result;
}

/* Обчислення провідності спінового транзистора Датта — Даса */
double simulate_datta_das_current(DattaDasParams p) {
    double alpha_j = p.alpha_r * EV_TO_JOULE;
    double delta_theta = (2.0 * p.m_eff * alpha_j * p.channel_length) / (HBAR * HBAR);
    
    /* Нормалізований струм: I / I_max = cos^2(Delta theta / 2) */
    double cos_val = cos(delta_theta / 2.0);
    return cos_val * cos_val;
}

int main(void) {
    printf("=== Таблиця істинності Магнонного Логічного Вентиля ===\n");
    printf("Phase A (rad) | Phase B (rad) | Intensity | XOR | AND\n");
    printf("------------------------------------------------------\n");

    double phases[2] = {0.0, M_PI};
    double threshold = 3.0; /* Поріг амплітуди для операції AND */

    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 2; j++) {
            MagnonWave w1 = {1.0, phases[i], 10.0e9};
            MagnonWave w2 = {1.0, phases[j], 10.0e9};

            MagnonicGateResult res = simulate_magnonic_gate(w1, w2, threshold);
            printf("    %4.2f      |     %4.2f     |   %5.3f   |  %d  |  %d\n",
                   res.input_phase_a, res.input_phase_b,
                   res.output_intensity, res.logic_bit_xor, res.logic_bit_and);
        }
    }

    printf("\n=== Моделювання Спінового FET Датта — Даса ===\n");
    DattaDasParams params;
    params.channel_length = 200.0e-9; /* 200 нм */
    params.m_eff = 0.023 * ME;         /* InAs канал */

    printf("Alpha_R (eV*m)  | Spin Precession Angle (rad) | Normalized Current I/I_max\n");
    printf("------------------------------------------------------------------------\n");

    for (double alpha = 0.0; alpha <= 2.0e-11; alpha += 0.4e-11) {
        params.alpha_r = alpha;
        double current = simulate_datta_das_current(params);
        double theta = (2.0 * params.m_eff * alpha * EV_TO_JOULE * params.channel_length) / (HBAR * HBAR);

        printf("  %8.2e     |           %6.3f           |         %6.4f\n",
               alpha, theta, current);
    }

    return 0;
}
