#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Фізичні константи */
#define K_BOLTZMANN_EV 8.617333262145e-5  /* Стала Больцмана в еВ/К */

/* Структура параметрів металізації */
typedef struct {
    double activation_energy_ev; /* Енергія активації E_a (еВ) */
    double current_exponent;     /* Показник ступеня Блека n */
    double blech_product_a_cm;   /* Критичний добуток Блеха (А/см) */
} metal_process_params_t;

/* Структура умов випробувань та експлуатації */
typedef struct {
    double temp_celsius;         /* Температура в градусах Цельсія */
    double current_density_a_cm2;/* Густина струму в А/см² */
} operating_condition_t;

/* Результати оцінки надійності */
typedef struct {
    double acceleration_factor;  /* Коефіцієнт прискорення AF */
    double mttf_use_hours;       /* Прогнозований MTTF за робочих умов (годин) */
    double critical_length_um;   /* Критична довжина Блеха L_c (мікрометрів) */
    bool is_blech_immune;        /* Прапорець імунітету за довжиною */
} reliability_result_t;

/* Перетворення градусів Цельсія у Кельвіни */
static inline double celsius_to_kelvin(double temp_c) {
    return temp_c + 273.15;
}

/* Обчислення коефіцієнта прискорення та терміну служби */
bool calculate_reliability(
    const metal_process_params_t *process,
    const operating_condition_t *test_cond,
    double mttf_test_hours,
    const operating_condition_t *use_cond,
    double line_length_um,
    reliability_result_t *out_result
) {
    if (!process || !test_cond || !use_cond || !out_result) {
        return false;
    }
    if (test_cond->current_density_a_cm2 <= 0.0 || use_cond->current_density_a_cm2 <= 0.0) {
        return false;
    }

    double t_test_k = celsius_to_kelvin(test_cond->temp_celsius);
    double t_use_k = celsius_to_kelvin(use_cond->temp_celsius);

    /* Складник прискорення за струмом */
    double current_ratio = test_cond->current_density_a_cm2 / use_cond->current_density_a_cm2;
    double j_factor = pow(current_ratio, process->current_exponent);

    /* Складник прискорення за температурою (Арреніус) */
    double temp_diff_inv = (1.0 / t_use_k) - (1.0 / t_test_k);
    double t_factor = exp((process->activation_energy_ev / K_BOLTZMANN_EV) * temp_diff_inv);

    /* Загальний коефіцієнт прискорення AF */
    out_result->acceleration_factor = j_factor * t_factor;
    out_result->mttf_use_hours = mttf_test_hours * out_result->acceleration_factor;

    /* Перевірка критерію Блеха (L_c в мікрометрах: (A/см / А/см²) * 10⁴ мкм/см) */
    out_result->critical_length_um = (process->blech_product_a_cm / use_cond->current_density_a_cm2) * 1.0e4;
    out_result->is_blech_immune = (line_length_um <= out_result->critical_length_um);

    return true;
}

int main(void) {
    /* Параметри мідної металізації Dual-Damascene (Cu з покриттям Co/Ru) */
    metal_process_params_t cu_process = {
        .activation_energy_ev = 0.90,  /* E_a = 0.9 еВ */
        .current_exponent = 1.5,       /* n = 1.5 */
        .blech_product_a_cm = 3500.0   /* (j·L)_c = 3500 А/см */
    };

    /* Умови випробування прискореного старіння HTOL */
    operating_condition_t htol_test = {
        .temp_celsius = 200.0,         /* T_test = 200 °C */
        .current_density_a_cm2 = 3.0e6 /* j_test = 3·10⁶ А/см² */
    };
    double mttf_test_h = 120.0;        /* Отриманий медіанний час відмови t50 = 120 годин */

    /* Робочі умови в інтегральній схемі */
    operating_condition_t operational_use = {
        .temp_celsius = 105.0,         /* T_use = 105 °C */
        .current_density_a_cm2 = 5.0e5 /* j_use = 5·10⁵ А/см² */
    };

    double interconnect_length_um = 50.0; /* Довжина доріжки 50 мкм */
    reliability_result_t res;

    if (calculate_reliability(&cu_process, &htol_test, mttf_test_h, &operational_use, interconnect_length_um, &res)) {
        printf("=== Результати аналізу електроміграційної надійності ===\n");
        printf("Коефіцієнт прискорення (AF): %.2f\n", res.acceleration_factor);
        printf("Прогнозований MTTF за робочих умов: %.2e годин (%.2f років)\n",
               res.mttf_use_hours, res.mttf_use_hours / 8760.0);
        printf("Критична довжина Блеха (L_c): %.2f мкм\n", res.critical_length_um);
        printf("Статус стійкості доріжки (50.0 мкм): %s\n",
               res.is_blech_immune ? "БЕЗСМЕРТНА (Immune)" : "ВРАЗЛИВА (Electromigration Limited)");
    }

    return 0;
}
