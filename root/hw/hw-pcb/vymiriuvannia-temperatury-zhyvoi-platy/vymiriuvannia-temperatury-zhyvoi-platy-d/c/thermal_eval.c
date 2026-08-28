/**
 * @file thermal_eval.c
 * @brief Перевірка теплових меж напівпровідникового компонента за JESD51.
 * Стандарт: C99.
 */

#include <stdio.h>
#include <stdbool.h>

typedef struct {
    float t_case_measured_c;  /* Виміряна контактним/оптичним способом температура кришки */
    float power_dissipated_w; /* Миттєва електрична потужність втрат у компоненті */
    float psi_jt;             /* Параметр теплової характеризації Psi-JT з datasheet (°C/Вт) */
    float t_junction_max_c;   /* Гранично допустима температура кристала T_J(max) */
    float safety_margin_c;    /* Необхідний інженерний запас надійності (зазвичай 15–20 °C) */
} thermal_eval_input_t;

typedef struct {
    float t_junction_est_c;   /* Оцінена внутрішня температура кристала T_J */
    float headroom_c;         /* Запас до граничної температури */
    bool is_safe;             /* Прапорець безпечної роботи */
} thermal_eval_result_t;

/**
 * @brief Розрахунок температури переходу T_J та перевірка теплового запасу.
 */
thermal_eval_result_t evaluate_junction_safety(const thermal_eval_input_t *in) {
    thermal_eval_result_t res;
    
    /* Розрахунок T_J за формулою стандарту JEDEC JESD51-2A */
    res.t_junction_est_c = in->t_case_measured_c + (in->psi_jt * in->power_dissipated_w);
    
    /* Розрахунок теплового запасу */
    res.headroom_c = in->t_junction_max_c - res.t_junction_est_c;
    
    /* Критерій безпеки: запас повинен перевищувати вимогу надійності */
    res.is_safe = (res.headroom_c >= in->safety_margin_c);
    
    return res;
}
