#include "afe_model.h"

#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846 /* поза POSIX math.h цієї константи може не бути */
#endif

/* --- Паспортні параметри тракту (розділи 2 і 4) --- */

#define V_REF          3.3       /* опорна напруга АЦП, В */
#define ADC_LEVELS     4096.0    /* 2^12 */
#define ADC_MAX        4095u

#define BRIDGE_SENS    0.0005    /* 2 мВ/В при збудженні 5 В і межі 20 кг -> 0.5 мВ/кг */
#define INAMP_R1       24700.0   /* внутрішні резистори AD620 */
#define INAMP_RG       330.0     /* зовнішній резистор підсилення */
#define V_SHIFT_NOM    1.65      /* штучна середня точка V_ref/2 на виводі REF */

/* --- Похибки конкретного примірника: те, заради чого існує калібрування --- */

#define GAIN_TOLERANCE 1.008     /* 0.8 % розкиду R_g і внутрішніх резисторів */
#define BRIDGE_OFFSET  0.00012   /* несиметрія моста, 0.12 мВ диференційно */
#define V_SHIFT_REAL   1.6478    /* дільник середньої точки теж не ідеальний */

/* --- Завади (розділи 2 і 3) --- */

#define MAINS_HZ       50.0
#define MAINS_DIFF_V   40.0e-6   /* залишок мережевої наводки ПІСЛЯ CMRR, диференційно */
#define PWM_HZ         980.0     /* комутація драйвера двигуна поруч на платі */
#define PWM_OUT_V      0.012     /* наводиться вже на вихідну доріжку, після підсилення */
#define NOISE_RMS_V    0.0004    /* тепловий шум тракту, СКВ на виході */

#define AAF_FC_HZ      500.0     /* зріз RC-ланки перед входом АЦП */

static double inamp_gain_nominal(void)
{
    return 1.0 + 2.0 * INAMP_R1 / INAMP_RG; /* G = 1 + 2*R1/R_g ≈ 150.7 */
}

/* xorshift64*: детермінований і однаковий на будь-якій платформі, на відміну від rand() */
static double noise_sample(afe_t *afe)
{
    afe->rng ^= afe->rng >> 12;
    afe->rng ^= afe->rng << 25;
    afe->rng ^= afe->rng >> 27;
    uint64_t bits = afe->rng * 2685821657736338717ull;

    /* рівномірний [-1, 1); СКВ рівномірного розподілу — a/sqrt(3), звідси множник */
    double u = (double)(bits >> 11) / 9007199254740992.0 * 2.0 - 1.0;
    return u * NOISE_RMS_V * 1.7320508;
}

/* Напруга на виході інструментального підсилювача просто зараз, до фільтра й АЦП. */
static double afe_output_voltage(afe_t *afe)
{
    const double gain = inamp_gain_nominal() * GAIN_TOLERANCE;

    /* Диференційний бік: корисний сигнал, несиметрія моста і те, що лишилося
       від мережевої наводки після придушення синфазної складової. */
    double v_diff = BRIDGE_SENS * afe->load_kg
                  + BRIDGE_OFFSET
                  + MAINS_DIFF_V * sin(2.0 * M_PI * MAINS_HZ * afe->t);

    /* Синфазні 2.5 В сюди не входять узагалі: In-Amp прибрав їх на 110 дБ. */
    double v_out = gain * v_diff + V_SHIFT_REAL;

    /* ШІМ наводиться на вихідну доріжку — підсилювач її вже не бачить,
       а от ключ вибірки АЦП побачить. */
    v_out += PWM_OUT_V * sin(2.0 * M_PI * PWM_HZ * afe->t);
    v_out += noise_sample(afe);

    return v_out;
}

static uint16_t quantize(double v)
{
    if (v <= 0.0) {
        return 0; /* вихід за шкалу знизу: АЦП більше нічого сказати не може */
    }
    double code = floor(v / V_REF * ADC_LEVELS);
    if (code >= (double)ADC_MAX) {
        return ADC_MAX; /* насичення шкали зверху */
    }
    return (uint16_t)code;
}

void afe_init(afe_t *afe, uint64_t seed, bool aaf_on)
{
    afe->t = 0.0;
    afe->load_kg = 0.0;
    afe->aaf_on = aaf_on;
    afe->rng = seed ? seed : 0x9E3779B97F4A7C15ull; /* нульове зерно вбило б xorshift */

    /* Фільтр стартує з усталеного значення, інакше перші мілісекунди
       моделі показували б не тракт, а заряд конденсатора. */
    afe->aaf_state = inamp_gain_nominal() * GAIN_TOLERANCE * BRIDGE_OFFSET + V_SHIFT_REAL;
}

void afe_set_load(afe_t *afe, double load_kg)
{
    afe->load_kg = load_kg;
}

uint16_t afe_step(afe_t *afe)
{
    double v_out = afe_output_voltage(afe);
    afe->t += AFE_STEP_S;

    if (!afe->aaf_on) {
        return quantize(v_out); /* тракт без ФНЧ: на ключ іде все, включно з 980 Гц */
    }

    /* Однополюсна RC-ланка в дискретній формі: alpha = dt / (RC + dt). */
    const double rc = 1.0 / (2.0 * M_PI * AAF_FC_HZ);
    const double alpha = AFE_STEP_S / (rc + AFE_STEP_S);

    afe->aaf_state += (v_out - afe->aaf_state) * alpha;
    return quantize(afe->aaf_state);
}

double afe_nominal_counts_per_kg(void)
{
    return inamp_gain_nominal() * BRIDGE_SENS * ADC_LEVELS / V_REF;
}
