#include "standoff_calc.h"
#include <stdio.h>

int main(void) {
    printf("=== Інженерний калькулятор міжплатних стійок (C99) ===\n");

    /* Тестовий випадок 1: Багатоплатний модуль живлення (M3, латунні стійки для заземлення) */
    pcb_stack_params_t power_board = {
        .max_component_height_mm = 8.50, // Електролітичний конденсатор
        .lead_protrusion_mm = 1.50,      // Хвостики THT компонентів
        .required_air_gap_mm = 1.50,     // Вентиляційний проміжок
        .pcb_deflection_mm = 0.30        // Можливий прогин плати FR-4
    };

    standoff_result_t power_result;
    standoff_calculate_clearance(&power_board, THREAD_M3, MATERIAL_BRASS_CW614N, &power_result);
    standoff_print_report(&power_board, THREAD_M3, MATERIAL_BRASS_CW614N, &power_result);

    /* Тестовий випадок 2: Чутлива цифрова плата з гальванічною розв'язкою (M2, нейлон PA66) */
    pcb_stack_params_t sensor_board = {
        .max_component_height_mm = 3.20, // Роз'єм micro-USB / сенсор
        .lead_protrusion_mm = 1.00,
        .required_air_gap_mm = 1.00,
        .pcb_deflection_mm = 0.20
    };

    standoff_result_t sensor_result;
    standoff_calculate_clearance(&sensor_board, THREAD_M2, MATERIAL_NYLON_PA66, &sensor_result);
    standoff_print_report(&sensor_board, THREAD_M2, MATERIAL_NYLON_PA66, &sensor_result);

    /* Перевірка безпеки крутного моменту */
    double test_torque = 0.35; // Спроба затягнути з моментом 0.35 Н*м
    printf("\nПеревірка монтажного моменту T = %.2f Н*м:\n", test_torque);
    
    bool brass_ok = standoff_is_torque_safe(THREAD_M3, MATERIAL_BRASS_CW614N, test_torque);
    printf(" - Для латуні M3: %s (межа 0.70 Н*м)\n", brass_ok ? "БЕЗПЕЧНО" : "РИЗИК ЗРИВУ");

    bool nylon_ok = standoff_is_torque_safe(THREAD_M3, MATERIAL_NYLON_PA66, test_torque);
    printf(" - Для нейлону M3: %s (межа 0.24 Н*м -> деформація різьби!)\n", nylon_ok ? "БЕЗПЕЧНО" : "НЕБЕЗПЕЧНО: ПЛАСТИЧНИЙ ЗРИВ");

    return 0;
}
