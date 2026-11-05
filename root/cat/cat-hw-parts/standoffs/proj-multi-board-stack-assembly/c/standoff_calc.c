#include "standoff_calc.h"
#include <stdio.h>
#include <string.h>

/* Стандартний виробничий ряд висот міжплатних стійок (мм) */
static const double STANDARD_HEIGHTS[] = {
    4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 15.0, 18.0, 20.0, 25.0, 30.0, 35.0, 40.0
};
static const size_t STANDARD_HEIGHTS_COUNT = sizeof(STANDARD_HEIGHTS) / sizeof(STANDARD_HEIGHTS[0]);

const double* standoff_get_standard_heights(size_t *count) {
    if (count) {
        *count = STANDARD_HEIGHTS_COUNT;
    }
    return STANDARD_HEIGHTS;
}

static void get_torque_limits(thread_size_t thread, standoff_material_t material, double *max_t, double *rec_t) {
    if (thread == THREAD_M2) {
        if (material == MATERIAL_BRASS_CW614N) {
            *max_t = 0.28; /* Н*м межа зриву латуні M2 */
            *rec_t = 0.22;
        } else {
            *max_t = 0.09; /* Н*м межа текучості нейлону PA66 M2 */
            *rec_t = 0.07;
        }
    } else { /* THREAD_M3 */
        if (material == MATERIAL_BRASS_CW614N) {
            *max_t = 0.70; /* Н*м межа зриву латуні M3 */
            *rec_t = 0.58;
        } else {
            *max_t = 0.24; /* Н*м межа нейлону PA66 M3 */
            *rec_t = 0.18;
        }
    }
}

void standoff_calculate_clearance(const pcb_stack_params_t *params, 
                                 thread_size_t thread, 
                                 standoff_material_t material, 
                                 standoff_result_t *result) {
    if (!params || !result) return;

    memset(result, 0, sizeof(standoff_result_t));

    /* Розрахунок мінімального зазору: h_min = h_comp + h_lead + h_air + delta */
    double h_min = params->max_component_height_mm + 
                   params->lead_protrusion_mm + 
                   params->required_air_gap_mm + 
                   params->pcb_deflection_mm;

    result->min_required_height_mm = h_min;

    /* Пошук найближчої стандартної висоти h_std >= h_min */
    result->selected_standard_height = -1.0;
    for (size_t i = 0; i < STANDARD_HEIGHTS_COUNT; ++i) {
        if (STANDARD_HEIGHTS[i] >= h_min) {
            result->selected_standard_height = STANDARD_HEIGHTS[i];
            break;
        }
    }

    if (result->selected_standard_height > 0.0) {
        result->is_valid = true;
        result->effective_clearance_mm = result->selected_standard_height - 
                                        (params->max_component_height_mm + params->lead_protrusion_mm);
    } else {
        /* Якщо компонування перевищує 40 мм, потрібні складові стійки */
        result->is_valid = false;
        result->selected_standard_height = 0.0;
        result->effective_clearance_mm = 0.0;
    }

    get_torque_limits(thread, material, &result->max_safe_torque_nm, &result->recommended_torque_nm);
}

bool standoff_is_torque_safe(thread_size_t thread, standoff_material_t material, double applied_torque_nm) {
    double max_t = 0.0;
    double rec_t = 0.0;
    get_torque_limits(thread, material, &max_t, &rec_t);
    return (applied_torque_nm <= max_t);
}

void standoff_print_report(const pcb_stack_params_t *params, 
                          thread_size_t thread, 
                          standoff_material_t material, 
                          const standoff_result_t *result) {
    if (!params || !result) return;

    printf("\n======================================================\n");
    printf("     РОЗРАХУНОК МІЖПЛАТНИХ СТІЙОК ДРУКОВАНОГО СТЕКА   \n");
    printf("======================================================\n");
    printf(" Різьба                      : %s\n", (thread == THREAD_M2) ? "M2 (крок 0.4 мм)" : "M3 (крок 0.5 мм)");
    printf(" Матеріал стійки             : %s\n", 
           (material == MATERIAL_BRASS_CW614N) ? "Латунь CW614N (провідна)" : "Поліамід PA66 (ізолювальна)");
    printf(" Максимальна висота деталі   : %.2f мм\n", params->max_component_height_mm);
    printf(" Виліт паяних виводів        : %.2f мм\n", params->lead_protrusion_mm);
    printf(" Нормативний ізоляційний шар : %.2f мм\n", params->required_air_gap_mm);
    printf(" Допуск на прогин текстоліту : %.2f мм\n", params->pcb_deflection_mm);
    printf("------------------------------------------------------\n");
    printf(" Мінімальна висота (h_min)   : %.2f мм\n", result->min_required_height_mm);

    if (result->is_valid) {
        printf(" Обрана висота з ряду (h_std): %.1f мм\n", result->selected_standard_height);
        printf(" Фактичний зазор безпеки     : %.2f мм\n", result->effective_clearance_mm);
        printf(" Рекомендований момент монтажу: %.2f Н*м\n", result->recommended_torque_nm);
        printf(" Граничний момент затягування: %.2f Н*м\n", result->max_safe_torque_nm);
        printf(" СТАТУС                      : [КОРЕКТНО] Зазор безпеки гарантовано.\n");
    } else {
        printf(" УВАГА: Висота перевищує максимальний стандарт 40 мм!\n");
        printf(" РЕКОМЕНДАЦІЯ: Використовувати збірку зі з'єднаних стійок тато-мама.\n");
    }
    printf("======================================================\n");
}
