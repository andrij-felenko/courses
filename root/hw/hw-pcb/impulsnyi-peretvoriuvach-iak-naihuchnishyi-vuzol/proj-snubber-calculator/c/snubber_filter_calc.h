/* snubber_filter_calc.h */
#ifndef SNUBBER_FILTER_CALC_H
#define SNUBBER_FILTER_CALC_H

#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    CALC_OK = 0,
    CALC_ERR_INVALID_FREQ,
    CALC_ERR_FREQ_NOT_DECREASED,
    CALC_ERR_INVALID_CAPACITANCE,
    CALC_ERR_INVALID_VOLTAGE,
    CALC_ERR_INVALID_POWER,
    CALC_ERR_MIDDLEBROOK_VIOLATION
} CalcStatus;

typedef struct {
    double f1_hz;          /* Початкова частота дзвону вузла SW (Гц) */
    double f2_hz;          /* Зміщена частота після додавання C_test (Гц) */
    double c_test_f;       /* Ємність тестового конденсатора (Ф) */
    double v_in_volts;     /* Вхідна напруга живлення DC-DC (В) */
    double f_sw_hz;        /* Робоча частота перемикання перетворювача (Гц) */
    double cap_multiplier; /* Множник ємності снубера k_c (типово 2.0..4.0) */
} SnubberInput;

typedef struct {
    double c_par_f;        /* Власна паразитна ємність вузла (Ф) */
    double l_par_h;        /* Власна паразитна індуктивність контуру (Гн) */
    double z0_ohms;        /* Характеристичний імпеданс паразитного контуру (Ом) */
    double r_snub_ideal;   /* Теоретичний опір резистора снубера (Ом) */
    double r_snub_e24;     /* Найближчий стандартний номінал з ряду E24 (Ом) */
    double c_snub_ideal;   /* Теоретична ємність снубера (Ф) */
    double c_snub_e24;     /* Найближча стандартна ємність з ряду E24 (Ф) */
    double p_loss_watts;   /* Активна потужність втрат на снубері (Вт) */
    double i_peak_amps;    /* Піковий імпульсний струм через резистор (А) */
    CalcStatus status;
} SnubberOutput;

typedef struct {
    double v_in_min_v;     /* Мінімальна вхідна напруга живлення (В) */
    double p_out_w;        /* Максимальна вихідна потужність навантаження (Вт) */
    double efficiency;     /* ККД перетворювача (0.5..0.99) */
    double f_sw_hz;        /* Частота комутації DC-DC (Гц) */
    double v_ripple_in_v;  /* Амплітуда пульсацій вхідного струму без фільтра (В) */
    double v_target_att_db;/* Бажане затухання вхідного фільтра на f_sw (дБ) */
    double l_filter_h;     /* Номінал обраного вхідного дроселя (Гн) */
} FilterInput;

typedef struct {
    double r_in_converter; /* Динамічний негативний вхідний опір DC-DC (Ом) */
    double f_cutoff_ideal; /* Необхідна частота зрізу фільтра (Гц) */
    double c_filter_ideal; /* Теоретична вихідна ємність фільтра C_2 (Ф) */
    double c_filter_e24;   /* Стандартна вихідна ємність C_2 (Ф) */
    double c_damping_ideal;/* Ємність демпфувального конденсатора C_d (Ф) */
    double c_damping_e12;  /* Стандартна ємність C_d (Ф) */
    double r_damping_ideal;/* Теоретичний опір демпфера R_d (Ом) */
    double r_damping_e24;  /* Стандартний опір R_d з ряду E24 (Ом) */
    double z_out_max_ohms; /* Максимальний демпфований вихідний імпеданс (Ом) */
    double stability_margin;/* Запас стійкості Міддлбрука |R_in| / Z_out_max */
    bool is_stable;        /* Прапорець виконання критерію Міддлбрука */
    CalcStatus status;
} FilterOutput;

SnubberOutput calculate_rc_snubber(const SnubberInput* input);
FilterOutput calculate_input_filter(const FilterInput* input);
double find_nearest_e24(double value);
double find_nearest_e96(double value);
double find_nearest_e12(double value);

#ifdef __cplusplus
}
#endif

#endif /* SNUBBER_FILTER_CALC_H */

/* snubber_filter_calc.c */
#include "snubber_filter_calc.h"
#include <math.h>

#define MATH_PI 3.14159265358979323846

static const double E24_BASE[24] = {
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
};

static const double E12_BASE[12] = {
    1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2
};

static double find_nearest_in_table(double val, const double* table, size_t count) {
    if (val <= 0.0) return 0.0;
    double exponent = floor(log10(val));
    double mantissa = val / pow(10.0, exponent);

    double best_diff = 1e9;
    double best_mantissa = table[0];

    for (size_t i = 0; i < count; ++i) {
        double diff = fabs(mantissa - table[i]);
        if (diff < best_diff) {
            best_diff = diff;
            best_mantissa = table[i];
        }
    }

    if (fabs(mantissa - 10.0) < best_diff) {
        best_mantissa = 1.0;
        exponent += 1.0;
    }

    return best_mantissa * pow(10.0, exponent);
}

double find_nearest_e24(double value) {
    return find_nearest_in_table(value, E24_BASE, 24);
}

double find_nearest_e12(double value) {
    return find_nearest_in_table(value, E12_BASE, 12);
}

double find_nearest_e96(double value) {
    if (value <= 0.0) return 0.0;
    double exponent = floor(log10(value));
    double mantissa = value / pow(10.0, exponent);
    
    double k = round(96.0 * log10(mantissa));
    if (k >= 96.0) {
        k = 0.0;
        exponent += 1.0;
    }
    double best_mantissa = round(pow(10.0, k / 96.0) * 100.0) / 100.0;
    return best_mantissa * pow(10.0, exponent);
}

SnubberOutput calculate_rc_snubber(const SnubberInput* in) {
    SnubberOutput out = {0};

    if (!in) {
        out.status = CALC_ERR_INVALID_FREQ;
        return out;
    }
    if (in->f1_hz <= 0.0 || in->f2_hz <= 0.0) {
        out.status = CALC_ERR_INVALID_FREQ;
        return out;
    }
    if (in->f2_hz >= in->f1_hz) {
        out.status = CALC_ERR_FREQ_NOT_DECREASED;
        return out;
    }
    if (in->c_test_f <= 0.0) {
        out.status = CALC_ERR_INVALID_CAPACITANCE;
        return out;
    }
    if (in->v_in_volts <= 0.0) {
        out.status = CALC_ERR_INVALID_VOLTAGE;
        return out;
    }

    double k_c = (in->cap_multiplier >= 1.0 && in->cap_multiplier <= 10.0) ? in->cap_multiplier : 3.0;

    /* Розрахунок власної паразитної ємності */
    double freq_ratio = in->f1_hz / in->f2_hz;
    double freq_ratio_sq = freq_ratio * freq_ratio;
    out.c_par_f = in->c_test_f / (freq_ratio_sq - 1.0);

    /* Розрахунок власної паразитної індуктивності */
    double omega1 = 2.0 * MATH_PI * in->f1_hz;
    out.l_par_h = 1.0 / (omega1 * omega1 * out.c_par_f);

    /* Характеристичний імпеданс контуру */
    out.z0_ohms = sqrt(out.l_par_h / out.c_par_f);

    /* Теоретичні номінали снубера */
    out.r_snub_ideal = out.z0_ohms;
    out.c_snub_ideal = k_c * out.c_par_f;

    /* Апроксимація до ряду E24 */
    out.r_snub_e24 = find_nearest_e24(out.r_snub_ideal);
    out.c_snub_e24 = find_nearest_e24(out.c_snub_ideal);

    /* Теплові втрати та піковий струм */
    out.p_loss_watts = out.c_snub_e24 * (in->v_in_volts * in->v_in_volts) * in->f_sw_hz;
    out.i_peak_amps = in->v_in_volts / out.r_snub_e24;
    out.status = CALC_OK;

    return out;
}

FilterOutput calculate_input_filter(const FilterInput* in) {
    FilterOutput out = {0};

    if (!in) {
        out.status = CALC_ERR_INVALID_VOLTAGE;
        return out;
    }
    if (in->v_in_min_v <= 0.0 || in->efficiency <= 0.0 || in->efficiency > 1.0) {
        out.status = CALC_ERR_INVALID_VOLTAGE;
        return out;
    }
    if (in->p_out_w <= 0.0) {
        out.status = CALC_ERR_INVALID_POWER;
        return out;
    }
    if (in->f_sw_hz <= 0.0 || in->l_filter_h <= 0.0) {
        out.status = CALC_ERR_INVALID_FREQ;
        return out;
    }

    /* Динамічний вхідний опір перетворювача */
    out.r_in_converter = (in->v_in_min_v * in->v_in_min_v * in->efficiency) / in->p_out_w;

    /* Частота зрізу фільтра */
    double att_db = (in->v_target_att_db > 0.0) ? in->v_target_att_db : 30.0;
    out.f_cutoff_ideal = in->f_sw_hz * pow(10.0, -att_db / 40.0);

    /* Необхідна вихідна ємність фільтра C_2 */
    double omega_c = 2.0 * MATH_PI * out.f_cutoff_ideal;
    out.c_filter_ideal = 1.0 / (omega_c * omega_c * in->l_filter_h);
    out.c_filter_e24 = find_nearest_e24(out.c_filter_ideal);

    /* Паралельне демпфування Міддлбрука (n = 4) */
    double n = 4.0;
    out.c_damping_ideal = n * out.c_filter_e24;
    out.c_damping_e12 = find_nearest_e12(out.c_damping_ideal);

    /* Оптимальний демпфувальний резистор */
    double z_char = sqrt(in->l_filter_h / out.c_filter_e24);
    double q_opt_factor = sqrt(((2.0 + n) * (4.0 + 3.0 * n)) / (2.0 * n * n * (4.0 + n)));
    out.r_damping_ideal = z_char * q_opt_factor;
    out.r_damping_e24 = find_nearest_e24(out.r_damping_ideal);

    /* Піковий вихідний опір демпфованого фільтра */
    out.z_out_max_ohms = z_char * (sqrt(2.0 * (2.0 + n)) / n);

    /* Перевірка критерію стійкості Міддлбрука */
    out.stability_margin = out.r_in_converter / out.z_out_max_ohms;
    out.is_stable = (out.stability_margin >= 3.0);
    out.status = out.is_stable ? CALC_OK : CALC_ERR_MIDDLEBROOK_VIOLATION;

    return out;
}
