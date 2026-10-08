#include <stdio.h>
#include <math.h>

// Структура параметрів інструментального підсилювача LVDT
typedef struct {
    double carrier_freq_hz;    // Несуча частота збудження (Гц)
    double v_diff_max_v;       // Максимальна амплітуда різниці V1 - V2 (В)
    double v_target_max_v;     // Цільова амплітуда для демодулятора (В)
    double opamp_gbp_hz;       // Добуток підсилення на смугу ОП (Гц)
    double r_feedback_ohm;     // Внутрішній опір зворотного зв'язку InAmp (Ом)
} inamp_config_t;

// Розрахунок резистора Rg та оцінка фазової похибки ОП
void calculate_inamp_stage(const inamp_config_t* cfg) {
    double g_required = cfg->v_target_max_v / cfg->v_diff_max_v;
    
    // Розрахунок зовнішнього резистора підсилення Rg = 2 * Rf / (G - 1)
    double r_gain = (2.0 * cfg->r_feedback_ohm) / (g_required - 1.0);
    
    // Оцінка граничної частоти підсилювача при заданому G
    double stage_bandwidth = cfg->opamp_gbp_hz / g_required;
    
    // Оцінка додаткового фазового зсуву ОП на несучій частоті: phi = -arctan(f_c / f_bw)
    double phase_error_rad = -atan(cfg->carrier_freq_hz / stage_bandwidth);
    double phase_error_deg = phase_error_rad * (180.0 / M_PI);

    printf("--- Розрахунок каскаду нормування InAmp ---\n");
    printf("Необхідний коефіцієнт підсилення G: %.2f\n", g_required);
    printf("Розрахунковий опір Rg: %.1f Ом\n", r_gain);
    printf("Смуга пропускання каскаду: %.1f кГц\n", stage_bandwidth / 1000.0);
    printf("Внесений фазовий зсув ОП: %.3f градусів\n", phase_error_deg);
}
