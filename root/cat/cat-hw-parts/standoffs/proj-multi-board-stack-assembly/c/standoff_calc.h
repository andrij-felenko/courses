#ifndef STANDOFF_CALC_H
#define STANDOFF_CALC_H

#include <stdbool.h>
#include <stddef.h>

/**
 * @brief Метричний типорозмір різьби міжплатної стійки.
 */
typedef enum {
    THREAD_M2,  ///< Метрична нарізь M2 x 0.4 мм
    THREAD_M3   ///< Метрична нарізь M3 x 0.5 мм
} thread_size_t;

/**
 * @brief Конструкційний матеріал стійки.
 */
typedef enum {
    MATERIAL_BRASS_CW614N,  ///< Свинцева латунь (CW614N) - провідна, екрануюча
    MATERIAL_NYLON_PA66     ///< Поліамід (Нейлон PA66) - діелектрик 20 кВ/мм
} standoff_material_t;

/**
 * @brief Вхідні геометричні параметри друкованої плати для розрахунку висоти стійки.
 */
typedef struct {
    double max_component_height_mm; ///< Найбільша висота компонента під платою (h_comp)
    double lead_protrusion_mm;      ///< Довжина виступання паяних ніжок THT (h_lead, зазвичай 1.0..2.0 мм)
    double required_air_gap_mm;     ///< Необхідний повітряний вентиляційний/ізоляційний зазор (h_air)
    double pcb_deflection_mm;       ///< Розрахунковий пружний прогин плати під навантаженням (delta)
} pcb_stack_params_t;

/**
 * @brief Результат підбору міжплатної стійки.
 */
typedef struct {
    double min_required_height_mm;  ///< Розрахована мінімальна висота (h_min)
    double selected_standard_height;///< Найближча більша стандартна висота з ряду
    double effective_clearance_mm;  ///< Фактичний залишковий зазор безпеки
    double max_safe_torque_nm;      ///< Граничний крутний момент затягування (Н*м)
    double recommended_torque_nm;   ///< Рекомендований робочий момент монтажу (Н*м)
    bool is_valid;                  ///< Ознака коректності підбору
} standoff_result_t;

/**
 * @brief Повертає масив стандартних висот стійок у міліметрах.
 */
const double* standoff_get_standard_heights(size_t *count);

/**
 * @brief Обчислює мінімальну необхідну висоту та обирає стандартну стійку з ряду.
 * @param params Геометричні параметри компонування плати.
 * @param thread Типорозмір різьби (M2 або M3).
 * @param material Матеріал стійки (латунь або нейлон).
 * @param result Вказівник на структуру результату.
 */
void standoff_calculate_clearance(const pcb_stack_params_t *params, 
                                 thread_size_t thread, 
                                 standoff_material_t material, 
                                 standoff_result_t *result);

/**
 * @brief Перевіряє безпечність прикладеного крутного моменту затягування.
 * @param thread Типорозмір нарізі.
 * @param material Матеріал виробу.
 * @param applied_torque_nm Фактичний крутний момент (Н*м).
 * @return true, якщо момент не перевищує 90% від межі зриву різьби.
 */
bool standoff_is_torque_safe(thread_size_t thread, standoff_material_t material, double applied_torque_nm);

/**
 * @brief Виводить форматований інженерний звіт підбору стійок у консоль.
 */
void standoff_print_report(const pcb_stack_params_t *params, 
                          thread_size_t thread, 
                          standoff_material_t material, 
                          const standoff_result_t *result);

#endif /* STANDOFF_CALC_H */
