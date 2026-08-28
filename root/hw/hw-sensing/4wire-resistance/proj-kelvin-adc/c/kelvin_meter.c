/* kelvin_meter.c — Вимірювач опору за чотирипровідною схемою (C99 / Embedded C) */
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Структура конфігурації вимірювального тракту */
typedef struct {
    float r_ref_ohm;            /* Опір опорного резистора R_ref, Ом */
    float excitation_current_a; /* Струм збудження I_ex, А */
    int32_t adc_max_code;       /* Максимальний код АЦП (2^23 - 1 для 24 біт) */
    float pga_gain;             /* Коефіцієнт підсилення PGA */
    bool ratiometric;           /* Режим: true - ратіометричний, false - абсолютний */
    float adc_vref_v;           /* Абсолютна опорна напруга (якщо ratiometric = false) */
} kelvin_config_t;

/* Структура результату вимірювання */
typedef struct {
    float resistance_ohm;       /* Обчислений опір R_x, Ом */
    float temperature_c;        /* Обчислена температура для PT100 (°C) */
    float thermal_emf_v;        /* Оцінене значення паразитної термо-ЕРС, В */
    bool valid;                 /* Прапор успішності вимірювання */
} kelvin_result_t;

/* Обчислення температури за рівнянням Календара-Ван Дюзена для PT100 (IEC 60751) */
static float pt100_to_temperature(float r_ohm) {
    const float R0 = 100.0f;
    const float A = 3.9083e-3f;
    const float B = -5.775e-7f;

    if (r_ohm >= R0) {
        /* Для T >= 0 °C: R(T) = R0 * (1 + A*T + B*T^2) */
        float discriminant = A * A - 4.0f * B * (1.0f - r_ohm / R0);
        if (discriminant < 0.0f) return -999.0f;
        return (-A + sqrtf(discriminant)) / (2.0f * B);
    } else {
        /* Спрощене наближення для T < 0 °C */
        return (r_ohm - R0) / (R0 * A);
    }
}

/* Обчислення опору за двома відліками АЦП (з реверсуванням струму) */
kelvin_result_t kelvin_calculate_measurement(const kelvin_config_t *cfg,
                                             int32_t raw_code_pos,
                                             int32_t raw_code_neg)
{
    kelvin_result_t res = {0};

    if (!cfg || cfg->r_ref_ohm <= 0.0f || cfg->pga_gain <= 0.0f || cfg->adc_max_code <= 0) {
        res.valid = false;
        return res;
    }

    float r_calculated = 0.0f;
    float v_emf = 0.0f;

    if (cfg->ratiometric) {
        /* Ратіометричний режим: R_x = R_ref * (N_pos - N_neg) / (2 * N_max * Gain) */
        float delta_code = ((float)raw_code_pos - (float)raw_code_neg) / 2.0f;
        float sum_code   = ((float)raw_code_pos + (float)raw_code_neg) / 2.0f;

        r_calculated = cfg->r_ref_ohm * (delta_code / ((float)cfg->adc_max_code * cfg->pga_gain));

        /* Оцінка термо-ЕРС в умовних Омах або Напрузі */
        float v_lsb = (cfg->excitation_current_a * cfg->r_ref_ohm) / (float)cfg->adc_max_code;
        v_emf = sum_code * v_lsb / cfg->pga_gain;
    } else {
        /* Абсолютний режим з фіксованою Vref */
        float lsb_volts = cfg->adc_vref_v / ((float)cfg->adc_max_code * cfg->pga_gain);
        float v_pos = (float)raw_code_pos * lsb_volts;
        float v_neg = (float)raw_code_neg * lsb_volts;

        float delta_v = (v_pos - v_neg) / 2.0f;
        r_calculated = delta_v / cfg->excitation_current_a;
        v_emf = (v_pos + v_neg) / 2.0f;
    }

    res.resistance_ohm = r_calculated;
    res.temperature_c = pt100_to_temperature(r_calculated);
    res.thermal_emf_v = v_emf;
    res.valid = true;

    return res;
}
