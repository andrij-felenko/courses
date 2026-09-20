#include "../include/rocker_panel.h"
#include <stdio.h>
#include <math.h>

double calculate_wire_resistance(const wire_spec_t *wire) {
    if (wire == NULL || wire->cross_section_mm2 <= 0.0 || wire->length_m < 0.0) {
        return -1.0;
    }
    /* R = rho * L / S */
    return (wire->resistivity_ohm_mm2_m * wire->length_m) / wire->cross_section_mm2;
}

double calculate_minimum_wire_section(double current_a, double max_density_a_mm2) {
    if (current_a <= 0.0 || max_density_a_mm2 <= 0.0) {
        return 0.0;
    }
    /* S_min = I / J_max */
    return current_a / max_density_a_mm2;
}

double calculate_voltage_drop(double current_a, double wire_resistance_ohm) {
    if (current_a < 0.0 || wire_resistance_ohm < 0.0) {
        return 0.0;
    }
    /* U_drop = I * R */
    return current_a * wire_resistance_ohm;
}

double calculate_contact_power_loss(double current_a, double contact_resistance_mohm) {
    if (current_a < 0.0 || contact_resistance_mohm < 0.0) {
        return 0.0;
    }
    /* P = I^2 * R_contact (R переводиться з мОм у Ом діленням на 1000) */
    double r_ohm = contact_resistance_mohm / 1000.0;
    return current_a * current_a * r_ohm;
}

bool calculate_panel_thermal_result(
    const rocker_switch_t *sw,
    const wire_spec_t *wire,
    double load_current_a,
    double ambient_temp_c,
    double max_allowed_voltage_drop_percent,
    panel_thermal_result_t *result
) {
    if (sw == NULL || wire == NULL || result == NULL) {
        return false;
    }

    /* 1. Розрахунок електричних параметрів провідника */
    result->wire_resistance_ohm = calculate_wire_resistance(wire);
    if (result->wire_resistance_ohm < 0.0) {
        return false;
    }

    result->voltage_drop_v = calculate_voltage_drop(load_current_a, result->wire_resistance_ohm);
    
    if (sw->rated_voltage_v > 0.0) {
        result->voltage_drop_percent = (result->voltage_drop_v / sw->rated_voltage_v) * 100.0;
    } else {
        result->voltage_drop_percent = 0.0;
    }

    result->current_density_a_mm2 = (wire->cross_section_mm2 > 0.0) 
        ? (load_current_a / wire->cross_section_mm2) : 0.0;

    /* 2. Розрахунок втрат потужності */
    result->contact_power_loss_w = calculate_contact_power_loss(load_current_a, sw->contact_resistance_mohm);
    result->wire_power_loss_w = load_current_a * load_current_a * result->wire_resistance_ohm;

    /* 3. Тепловий розрахунок перегріву корпусу рокера */
    /* Delta_T = P_loss * R_th */
    result->temperature_rise_c = result->contact_power_loss_w * sw->thermal_resistance_cw;
    result->final_temperature_c = ambient_temp_c + result->temperature_rise_c;

    /* 4. Перевірка нормативних критеріїв безпеки */
    result->is_thermal_safe = (result->final_temperature_c <= sw->max_allowed_temp_c);
    result->is_voltage_drop_safe = (result->voltage_drop_percent <= max_allowed_voltage_drop_percent);
    result->is_current_density_safe = (result->current_density_a_mm2 <= wire->max_current_density_a_mm2);
    result->is_current_rated_safe = (load_current_a <= sw->rated_current_a);

    return (result->is_thermal_safe && 
            result->is_voltage_drop_safe && 
            result->is_current_density_safe && 
            result->is_current_rated_safe);
}

void print_panel_thermal_report(
    const rocker_switch_t *sw,
    const wire_spec_t *wire,
    double load_current_a,
    double ambient_temp_c,
    const panel_thermal_result_t *result
) {
    if (sw == NULL || wire == NULL || result == NULL) {
        printf("ПОМИЛКА: Некоректні вказівники для формування звіту!\n");
        return;
    }

    printf("=================================================================\n");
    printf("        ЗВІТ ДІАГНОСТИКИ СИЛОВОЇ РОКЕРНОЇ ПАНЕЛІ КОМУТАЦІЇ      \n");
    printf("=================================================================\n");
    printf(" Вхідні параметри системи:\n");
    printf("  - Номінальна напруга кола:           %.1f В\n", sw->rated_voltage_v);
    printf("  - Номінальний струм перемикача:     %.1f А\n", sw->rated_current_a);
    printf("  - Опір контактної групи:            %.2f мОм\n", sw->contact_resistance_mohm);
    printf("  - Довжина силової лінії:            %.2f м\n", wire->length_m);
    printf("  - Переріз провідника:               %.2f мм²\n", wire->cross_section_mm2);
    printf("  - Фактичний струм навантаження:     %.2f А\n", load_current_a);
    printf("  - Температура довкілля:             %.1f °C\n", ambient_temp_c);
    printf("-----------------------------------------------------------------\n");
    printf(" Результати обчислення електричних режимів:\n");
    printf("  - Опір провідника лінії:             %.4f Ом\n", result->wire_resistance_ohm);
    printf("  - Спад напруги на лініях:            %.3f В (%.2f%%)\n", 
           result->voltage_drop_v, result->voltage_drop_percent);
    printf("  - Густина струму у провіднику:       %.2f А/мм² (макс: %.2f А/мм²)\n", 
           result->current_density_a_mm2, wire->max_current_density_a_mm2);
    printf("-----------------------------------------------------------------\n");
    printf(" Результати теплового розрахунку:\n");
    printf("  - Потужність втрат на контактах:     %.3f Вт\n", result->contact_power_loss_w);
    printf("  - Джоулеві втрати в провідниках:     %.3f Вт\n", result->wire_power_loss_w);
    printf("  - Перегрів корпусу (Delta T):        %.2f °C\n", result->temperature_rise_c);
    printf("  - Підсумкова температура корпусу:   %.2f °C (макс: %.1f °C)\n", 
           result->final_temperature_c, sw->max_allowed_temp_c);
    printf("-----------------------------------------------------------------\n");
    printf(" Перевірка вимог безпеки:\n");
    printf("  [1] Допустимість струму контакту:    %s\n", 
           result->is_current_rated_safe ? "ОК (струм у межах норми)" : "ПОМИЛКА (ПЕРЕВЕНТАЖЕННЯ!)");
    printf("  [2] Густина струму провідника:       %s\n", 
           result->is_current_density_safe ? "ОК (переріз достатній)" : "ПОМИЛКА (ПЕРЕГРІВ ЖИЛИ!)");
    printf("  [3] Допустимий спад напруги:        %s\n", 
           result->is_voltage_drop_safe ? "ОК (падіння у межах норми)" : "ПОМИЛКА (ПРОВАЛ НАПРУГИ!)");
    printf("  [4] Тепловий режим корпусу:         %s\n", 
           result->is_thermal_safe ? "ОК (температура в нормі)" : "ПОМИЛКА (ЗАГРОЗА ОПЛАВЛЕННЯ!)");
    printf("=================================================================\n\n");
}
