#include <stdio.h>
#include "../include/rocker_panel.h"

int main(void) {
    printf("=== МОДЕЛЮВАННЯ СИЛОВИХ РОКЕРНИХ ПАНЕЛЕЙ КОМУТАЦІЇ ===\n\n");

    /* -----------------------------------------------------------------
     * Сценарій 1: Промислова мережа змінного струму 230V AC (Навантаження 12A)
     * ----------------------------------------------------------------- */
    printf(">>> ТЕСТ 1: Рокерний перемикач 230V AC у шафі керування <<<\n");
    rocker_switch_t ac_switch = {
        .contact_resistance_mohm = 15.0,  /* 15 мОм */
        .rated_current_a = 16.0,          /* 16 А номінал */
        .rated_voltage_v = 230.0,         /* 230 В змінного струму */
        .thermal_resistance_cw = 18.0,    /* 18 °C/Вт R_th */
        .max_allowed_temp_c = 85.0        /* Макс 85 °C */
    };

    wire_spec_t ac_wire = {
        .length_m = 10.0,                          /* 10 метрів кабелю */
        .cross_section_mm2 = 1.5,                  /* Переріз 1.5 мм² */
        .resistivity_ohm_mm2_m = COPPER_RESISTIVITY_OHM_MM2_M,
        .max_current_density_a_mm2 = DEFAULT_MAX_CURRENT_DENSITY
    };

    double ac_load_current = 12.0; /* 12 А */
    double ac_ambient_temp = 35.0; /* 35 °C у шафі */
    double ac_max_voltage_drop_pct = 3.0; /* Макс 3% падіння напруги */

    panel_thermal_result_t ac_result;
    bool ac_status = calculate_panel_thermal_result(
        &ac_switch, &ac_wire, ac_load_current, ac_ambient_temp, ac_max_voltage_drop_pct, &ac_result
    );

    print_panel_thermal_report(&ac_switch, &ac_wire, ac_load_current, ac_ambient_temp, &ac_result);
    if (ac_status) {
        printf("ВИСНОВОК: Панель 230V AC відповідає нормам електро- та теплобезпеки.\n\n");
    } else {
        printf("УВАГА: Панель 230V AC НЕ відповідає нормам безпеки!\n\n");
    }

    /* -----------------------------------------------------------------
     * Сценарій 2: Низьковольтна силова мережа 24V DC (Навантаження 18A, тонкий дріт)
     * ----------------------------------------------------------------- */
    printf(">>> ТЕСТ 2: Низьковольтна лінія 24V DC із підвищеним навантаженням <<<\n");
    rocker_switch_t dc_switch = {
        .contact_resistance_mohm = 30.0,  /* 30 мОм (значне зношення контактів) */
        .rated_current_a = 20.0,          /* 20 А номінал */
        .rated_voltage_v = 24.0,          /* 24 В постійного струму */
        .thermal_resistance_cw = 25.0,    /* 25 °C/Вт R_th */
        .max_allowed_temp_c = 85.0        /* Макс 85 °C */
    };

    wire_spec_t dc_wire = {
        .length_m = 8.0,                           /* 8 метрів ліній */
        .cross_section_mm2 = 1.0,                  /* Занадто тонкий переріз 1.0 мм² */
        .resistivity_ohm_mm2_m = COPPER_RESISTIVITY_OHM_MM2_M,
        .max_current_density_a_mm2 = DEFAULT_MAX_CURRENT_DENSITY
    };

    double dc_load_current = 18.0; /* 18 А струм навантаження */
    double dc_ambient_temp = 40.0; /* 40 °C у важких умовах */
    double dc_max_voltage_drop_pct = 5.0; /* Макс 5% допустимий спад */

    panel_thermal_result_t dc_result;
    bool dc_status = calculate_panel_thermal_result(
        &dc_switch, &dc_wire, dc_load_current, dc_ambient_temp, dc_max_voltage_drop_pct, &dc_result
    );

    print_panel_thermal_report(&dc_switch, &dc_wire, dc_load_current, dc_ambient_temp, &dc_result);
    if (dc_status) {
        printf("ВИСНОВОК: Панель 24V DC відповідає нормам безпеки.\n\n");
    } else {
        printf("УВАГА: Виявлено критичні відхилення режиму 24V DC!\n");
        double min_section = calculate_minimum_wire_section(dc_load_current, dc_wire.max_current_density_a_mm2);
        printf("РЕКОМЕНДАЦІЯ: Збільшити переріз провідника щонайменше до %.2f мм² (поточний: %.2f мм²).\n\n",
               min_section, dc_wire.cross_section_mm2);
    }

    return 0;
}
