#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CELL_COUNT_MAX 16
#define NTC_COUNT_MAX  4

typedef struct {
    uint16_t cell_voltage_mv[CELL_COUNT_MAX];
    uint8_t  active_cells;
    int16_t  temperature_c[NTC_COUNT_MAX];
    uint8_t  active_ntc;
    int32_t  pack_current_ma;
} pack_metrics_t;

typedef struct {
    uint16_t max_allowed_imbalance_mv;
    uint16_t cell_ovp_threshold_mv;
    uint16_t cell_uvp_threshold_mv;
    int16_t  max_charge_temp_c;
    int16_t  min_charge_temp_c;
    int16_t  max_temp_gradient_c;
} safety_limits_t;

typedef struct {
    bool charge_allowed;
    bool discharge_allowed;
    bool balance_needed;
    uint16_t max_imbalance_mv;
    int16_t  max_gradient_c;
    uint8_t  highest_cell_idx;
    uint8_t  lowest_cell_idx;
} validation_result_t;

validation_result_t evaluate_pack_safety(const pack_metrics_t *metrics, 
                                        const safety_limits_t *limits) {
    validation_result_t res;
    memset(&res, 0, sizeof(validation_result_t));
    
    if (metrics->active_cells == 0 || metrics->active_cells > CELL_COUNT_MAX) {
        return res; /* Заборона всіх операцій при некоректній конфігурації */
    }

    uint16_t v_min = 0xFFFF;
    uint16_t v_max = 0;
    
    for (uint8_t i = 0; i < metrics->active_cells; ++i) {
        uint16_t v = metrics->cell_voltage_mv[i];
        if (v < v_min) {
            v_min = v;
            res.lowest_cell_idx = i;
        }
        if (v > v_max) {
            v_max = v;
            res.highest_cell_idx = i;
        }
    }
    
    res.max_imbalance_mv = v_max - v_min;
    
    int16_t t_min = 30000;
    int16_t t_max = -30000;
    for (uint8_t i = 0; i < metrics->active_ntc; ++i) {
        int16_t t = metrics->temperature_c[i];
        if (t < t_min) t_min = t;
        if (t > t_max) t_max = t;
    }
    res.max_gradient_c = (metrics->active_ntc > 0) ? (t_max - t_min) : 0;

    /* Перевірка критеріїв безпеки */
    bool v_ok = (v_min >= limits->cell_uvp_threshold_mv) && 
                (v_max <= limits->cell_ovp_threshold_mv);
    bool delta_v_ok = (res.max_imbalance_mv <= limits->max_allowed_imbalance_mv);
    bool temp_chg_ok = (t_max <= limits->max_charge_temp_c) && 
                       (t_min >= limits->min_charge_temp_c);
    bool grad_ok = (res.max_gradient_c <= limits->max_temp_gradient_c);

    if (v_ok && delta_v_ok && temp_chg_ok && grad_ok) {
        res.charge_allowed = true;
    }
    
    if (v_min >= limits->cell_uvp_threshold_mv && t_max <= 60 && grad_ok) {
        res.discharge_allowed = true;
    }

    if (res.max_imbalance_mv > 15 && v_max >= 4150) {
        res.balance_needed = true;
    }

    return res;
}
