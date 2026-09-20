#include "attenuator_calc.h"
#include <math.h>
#include <float.h>

// Базові значення ряду E24 (24 значення на декаду)
static const double E24_BASE[] = {
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
};
static const size_t E24_COUNT = sizeof(E24_BASE) / sizeof(E24_BASE[0]);

// Базові значення ряду E96 (96 значень на декаду)
static const double E96_BASE[] = {
    1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30,
    1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74,
    1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32,
    2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
    3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
    4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49,
    5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32,
    7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76
};
static const size_t E96_COUNT = sizeof(E96_BASE) / sizeof(E96_BASE[0]);

double find_nearest_eseries(double value_ohm, eseries_type_t series) {
    if (series == ESERIES_NONE || value_ohm <= 0.0) {
        return value_ohm;
    }

    const double *base_table = NULL;
    size_t count = 0;

    if (series == ESERIES_E24) {
        base_table = E24_BASE;
        count = E24_COUNT;
    } else if (series == ESERIES_E96) {
        base_table = E96_BASE;
        count = E96_COUNT;
    } else {
        return value_ohm;
    }

    double decade = floor(log10(value_ohm));
    double multiplier = pow(10.0, decade);
    double normalized = value_ohm / multiplier;

    double min_diff = DBL_MAX;
    double best_base = base_table[0];

    for (size_t i = 0; i < count; i++) {
        double diff = fabs(normalized - base_table[i]);
        if (diff < min_diff) {
            min_diff = diff;
            best_base = base_table[i];
        }
    }

    // Перевірка наближення до 10.0 (перехід на наступну декаду)
    double diff_next_decade = fabs(normalized - 10.0);
    if (diff_next_decade < min_diff) {
        return 1.0 * pow(10.0, decade + 1.0);
    }

    return best_base * multiplier;
}

bool attenuator_calculate(const attenuator_config_t *config,
                         attenuator_step_t *steps_out,
                         size_t max_steps_out,
                         size_t *actual_steps_count) {
    if (!config || !steps_out || !actual_steps_count) {
        return false;
    }

    if (config->num_steps < 2 || config->total_resistance_ohm <= 0.0) {
        return false;
    }

    size_t steps = config->num_steps;
    if (steps > max_steps_out) {
        steps = max_steps_out;
    }
    *actual_steps_count = steps;

    double ideal_r_bottom[ATTENUATOR_MAX_STEPS] = {0};
    double actual_resistors[ATTENUATOR_MAX_STEPS] = {0};

    // 1. Обчислення цільового згасання та теоретичних кумулятивних опорів нижнього плеча
    for (size_t i = 0; i < steps; i++) {
        double ideal_db = 0.0;
        double gain = 1.0;

        if (i == 0) {
            ideal_db = config->max_attenuation_db;
        } else if (i == steps - 1) {
            ideal_db = 0.0;
        } else {
            if (config->taper == ATTENUATION_LOGARITHMIC) {
                double db_step = (0.0 - config->max_attenuation_db) / (double)(steps - 1);
                ideal_db = config->max_attenuation_db + (double)i * db_step;
            } else if (config->taper == ATTENUATION_LINEAR) {
                gain = (double)i / (double)(steps - 1);
                ideal_db = (gain > 0.0) ? 20.0 * log10(gain) : config->max_attenuation_db;
            } else { // ATTENUATION_ANTILOGARITHMIC
                double norm = (double)i / (double)(steps - 1);
                gain = norm * norm;
                ideal_db = (gain > 0.0) ? 20.0 * log10(gain) : config->max_attenuation_db;
            }
        }

        if (config->taper == ATTENUATION_LOGARITHMIC) {
            gain = pow(10.0, ideal_db / 20.0);
        }

        steps_out[i].step_index = i;
        steps_out[i].ideal_attenuation_db = ideal_db;
        ideal_r_bottom[i] = config->total_resistance_ohm * gain;
    }

    // 2. Обчислення ідеальних та апроксимованих опорів кожної секції драбини
    steps_out[0].ideal_resistor_ohm = ideal_r_bottom[0];
    steps_out[0].actual_resistor_ohm = find_nearest_eseries(ideal_r_bottom[0], config->eseries);
    actual_resistors[0] = steps_out[0].actual_resistor_ohm;

    for (size_t i = 1; i < steps; i++) {
        double ideal_r_section = ideal_r_bottom[i] - ideal_r_bottom[i - 1];
        if (ideal_r_section < 0.0) {
            ideal_r_section = 0.0;
        }

        steps_out[i].ideal_resistor_ohm = ideal_r_section;
        steps_out[i].actual_resistor_ohm = find_nearest_eseries(ideal_r_section, config->eseries);
        actual_resistors[i] = steps_out[i].actual_resistor_ohm;
    }

    // 3. Обчислення фактичного згасання та відносної похибки з урахуванням імпедансів R_s і R_L
    double actual_r_total_sum = 0.0;
    for (size_t j = 0; j < steps; j++) {
        actual_r_total_sum += actual_resistors[j];
    }

    double actual_r_bottom_sum = 0.0;
    for (size_t i = 0; i < steps; i++) {
        actual_r_bottom_sum += actual_resistors[i];
        double r_bottom = actual_r_bottom_sum;
        double r_top = actual_r_total_sum - r_bottom;

        // Враховуємо паралельне навантаження R_L
        double r_bottom_eff = r_bottom;
        if (config->load_impedance_ohm > 0.0) {
            r_bottom_eff = (r_bottom * config->load_impedance_ohm) / (r_bottom + config->load_impedance_ohm);
        }

        // Загальний опір кола дільника з урахуванням R_s
        double total_circuit_r = config->source_impedance_ohm + r_top + r_bottom_eff;
        double actual_gain = 0.0;
        if (total_circuit_r > 0.0) {
            actual_gain = r_bottom_eff / total_circuit_r;
        }

        if (actual_gain > 0.0) {
            steps_out[i].actual_attenuation_db = 20.0 * log10(actual_gain);
        } else {
            steps_out[i].actual_attenuation_db = -120.0;
        }

        steps_out[i].error_db = steps_out[i].actual_attenuation_db - steps_out[i].ideal_attenuation_db;
        if (fabs(steps_out[i].ideal_attenuation_db) > 1e-6) {
            steps_out[i].error_percent = (steps_out[i].error_db / fabs(steps_out[i].ideal_attenuation_db)) * 100.0;
        } else {
            steps_out[i].error_percent = steps_out[i].error_db * 100.0;
        }
    }

    return true;
}
