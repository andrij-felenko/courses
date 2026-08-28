#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* Швидкісні режими за NXP UM10204 */
typedef enum {
    I2C_MODE_STANDARD,   /* 100 кГц, tr_max = 1000 нс, Cb_max = 400 пФ, Iol = 3 мА */
    I2C_MODE_FAST,       /* 400 кГц, tr_max = 300 нс,  Cb_max = 400 пФ, Iol = 3 мА */
    I2C_MODE_FAST_PLUS   /* 1 МГц,   tr_max = 120 нс,  Cb_max = 550 пФ, Iol = 20 мА */
} i2c_bus_mode_t;

/* Вхідні параметри конфігурації шини */
typedef struct {
    double vdd_volts;            /* Напруга живлення (наприклад, 3.3 В) */
    i2c_bus_mode_t mode;         /* Швидкісний режим */
    int chip_count;              /* Кількість мікросхем на шині (MCU + ведені) */
    double pcb_trace_length_cm;  /* Загальна довжина доріжки PCB (см) */
    double cable_length_m;       /* Довжина зовнішнього кабелю (м) */
    int connector_count;         /* Кількість рознімних з'єднань */
} i2c_bus_config_t;

/* Результати інженерного розрахунку */
typedef struct {
    double total_capacitance_pf; /* Сумарна розрахована ємність Cb (пФ) */
    double rp_min_ohms;          /* Нижня межа опору підтяжки (Ом) */
    double rp_max_ohms;          /* Верхня межа опору підтяжки (Ом) */
    double rp_recommended_ohms;  /* Рекомендований номінал з ряду E24 (Ом) */
    double actual_rise_time_ns;  /* Розрахунковий час наростання tr (нс) */
    double static_power_mw;      /* Статична розсіювана потужність на лінію (мВт) */
    bool is_valid_window;        /* Чи існує фізично припустиме вікно Rp */
    bool exceeds_standard_cb;    /* Чи перевищено норматив Cb для даного режиму */
} i2c_calc_result_t;

/* Стандартний ряд E24 (базові мантиси) */
static const double E24_SERIES[] = {
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
};
static const int E24_COUNT = sizeof(E24_SERIES) / sizeof(E24_SERIES[0]);

/* Підбір найближчого стандартного номіналу E24 у межах діапазону */
static double find_e24_resistor(double r_min, double r_max) {
    /* Цільове значення — зсунуте до нижньої третини вікна для запасу по tr */
    double target = r_min * 1.25;
    if (target > r_max) {
        target = (r_min + r_max) / 2.0;
    }

    double best_val = -1.0;
    double min_diff = 1e9;

    for (int dec = 1; dec <= 5; ++dec) {
        double mult = pow(10.0, dec);
        for (int i = 0; i < E24_COUNT; ++i) {
            double candidate = E24_SERIES[i] * mult;
            /* З урахуванням допуску ±5% */
            double worst_low = candidate * 0.95;
            double worst_high = candidate * 1.05;

            if (worst_low >= r_min && worst_high <= r_max) {
                double diff = fabs(candidate - target);
                if (diff < min_diff) {
                    min_diff = diff;
                    best_val = candidate;
                }
            }
        }
    }

    return best_val;
}

/* Головна функція розрахунку параметрів шини I2C */
bool i2c_calculate_pullup(const i2c_bus_config_t *cfg, i2c_calc_result_t *res) {
    if (!cfg || !res) return false;

    /* Типові питомі ємності компонентів */
    const double C_PIN_PER_CHIP_PF = 10.0;    /* 10 пФ на вивід за UM10204 */
    const double C_PCB_PER_CM_PF = 1.3;       /* 1.3 пФ/см для стандартного FR-4 */
    const double C_CABLE_PER_M_PF = 75.0;     /* 75 пФ/м для стрічкового шлейфу */
    const double C_CONNECTOR_PF = 2.0;        /* 2 пФ на рознім */

    /* 1. Сумарна ємність шини */
    res->total_capacitance_pf = (cfg->chip_count * C_PIN_PER_CHIP_PF) +
                                (cfg->pcb_trace_length_cm * C_PCB_PER_CM_PF) +
                                (cfg->cable_length_m * C_CABLE_PER_M_PF) +
                                (cfg->connector_count * C_CONNECTOR_PF);

    /* 2. Параметри швидкісного режиму */
    double tr_max_ns = 1000.0;
    double cb_limit_pf = 400.0;
    double iol_max_amps = 0.003;
    double vol_max_volts = 0.4;

    switch (cfg->mode) {
        case I2C_MODE_STANDARD:
            tr_max_ns = 1000.0;
            cb_limit_pf = 400.0;
            iol_max_amps = 0.003;
            break;
        case I2C_MODE_FAST:
            tr_max_ns = 300.0;
            cb_limit_pf = 400.0;
            iol_max_amps = 0.003;
            break;
        case I2C_MODE_FAST_PLUS:
            tr_max_ns = 120.0;
            cb_limit_pf = 550.0;
            iol_max_amps = 0.020;
            break;
    }

    if (cfg->vdd_volts <= 2.0) {
        vol_max_volts = 0.2 * cfg->vdd_volts;
    }

    res->exceeds_standard_cb = (res->total_capacitance_pf > cb_limit_pf);

    /* 3. Розрахунок меж Rp */
    res->rp_min_ohms = (cfg->vdd_volts - vol_max_volts) / iol_max_amps;

    const double LN_7_3 = 0.84729786;
    double cb_farads = res->total_capacitance_pf * 1e-12;
    double tr_max_sec = tr_max_ns * 1e-9;
    res->rp_max_ohms = tr_max_sec / (LN_7_3 * cb_farads);

    /* 4. Перевірка валідності вікна */
    if (res->rp_min_ohms <= res->rp_max_ohms) {
        res->is_valid_window = true;
        res->rp_recommended_ohms = find_e24_resistor(res->rp_min_ohms, res->rp_max_ohms);

        if (res->rp_recommended_ohms > 0.0) {
            res->actual_rise_time_ns = LN_7_3 * res->rp_recommended_ohms * cb_farads * 1e9;
            res->static_power_mw = (pow(cfg->vdd_volts - vol_max_volts, 2.0) / res->rp_recommended_ohms) * 1000.0;
        } else {
            /* Не знайшли резистор із запасом ±5%, беремо середнє арифметичне */
            res->rp_recommended_ohms = (res->rp_min_ohms + res->rp_max_ohms) / 2.0;
            res->actual_rise_time_ns = LN_7_3 * res->rp_recommended_ohms * cb_farads * 1e9;
            res->static_power_mw = (pow(cfg->vdd_volts - vol_max_volts, 2.0) / res->rp_recommended_ohms) * 1000.0;
        }
    } else {
        res->is_valid_window = false;
        res->rp_recommended_ohms = 0.0;
        res->actual_rise_time_ns = 0.0;
        res->static_power_mw = 0.0;
    }

    return true;
}

int main(void) {
    i2c_bus_config_t bus_cfg = {
        .vdd_volts = 3.3,
        .mode = I2C_MODE_FAST,          /* Fast-mode 400 кГц */
        .chip_count = 5,                /* 1 MCU + 4 сенсори */
        .pcb_trace_length_cm = 20.0,    /* 20 см траси */
        .cable_length_m = 0.8,          /* 80 см кабелю до модуля */
        .connector_count = 2
    };

    i2c_calc_result_t result;
    if (i2c_calculate_pullup(&bus_cfg, &result)) {
        printf("=== Результати розрахунку шини I2C ===\n");
        printf("Сумарна ємність Cb:      %.1f пФ\n", result.total_capacitance_pf);
        printf("Перевищення ліміту Cb:   %s\n", result.exceeds_standard_cb ? "ТАК (НЕБЕЗПЕЧНО)" : "НІ");
        printf("Діапазон підтяжки:       [%.0f Ом ... %.0f Ом]\n", result.rp_min_ohms, result.rp_max_ohms);

        if (result.is_valid_window) {
            printf("Рекомендований номінал:  %.0f Ом (E24)\n", result.rp_recommended_ohms);
            printf("Очікуваний час tr:       %.1f нс (ліміт: 300 нс)\n", result.actual_rise_time_ns);
            printf("Статична потужність:     %.2f мВт на лінію\n", result.static_power_mw);
        } else {
            printf("ПОМИЛКА: Вікно значень Rp замкнене! Потрібен буфер або зниження ємності.\n");
        }
    }

    return 0;
}
