#include <stdint.h>
#include <stdbool.h>

typedef struct {
    float sens_mv_per_mt;   /* Номінальна чутливість (мВ/мТл) */
    float temp_coeff_ppm;   /* Температурний коефіцієнт (ppm/°C) */
    float v_zero_volts;     /* Спокійна напруга нуля поля (В) */
    float b_op_mt;          /* Поріг спрацьовування компаратора (мТл) */
    float b_rp_mt;          /* Поріг відпускання компаратора (мТл) */
} hall_config_t;

typedef struct {
    hall_config_t cfg;
    bool switch_state;
    float current_field_mt;
} hall_driver_t;

void hall_driver_init(hall_driver_t *dev, const hall_config_t *cfg) {
    if (!dev || !cfg) return;
    dev->cfg = *cfg;
    dev->switch_state = false;
    dev->current_field_mt = 0.0f;
}

/**
 * Обробка 4 квадратурних фаз обертання струму для усунення офсету
 */
float hall_read_field_mt(hall_driver_t *dev, const float v_phases[4], float temp_c) {
    if (!dev || !v_phases) return 0.0f;

    /* 4-фазне обертання струму знищує постійний офсет кристала */
    float v_hall = (v_phases[0] - v_phases[1] + v_phases[2] - v_phases[3]) * 0.25f;
    float v_diff_mv = (v_hall - dev->cfg.v_zero_volts) * 1000.0f;

    /* Температурна компенсація чутливості */
    float temp_delta = temp_c - 25.0f;
    float sens_comp = dev->cfg.sens_mv_per_mt * (1.0f + (dev->cfg.temp_coeff_ppm * 1e-6f * temp_delta));

    if (sens_comp < 0.001f) sens_comp = 0.001f;

    dev->current_field_mt = v_diff_mv / sens_comp;

    /* Гістерезисна логіка цифрового перемикача */
    if (!dev->switch_state) {
        if (dev->current_field_mt >= dev->cfg.b_op_mt) {
            dev->switch_state = true;
        }
    } else {
        if (dev->current_field_mt <= dev->cfg.b_rp_mt) {
            dev->switch_state = false;
        }
    }

    return dev->current_field_mt;
}
