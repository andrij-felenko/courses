#ifndef ROCKER_PANEL_H
#define ROCKER_PANEL_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file rocker_panel.h
 * @brief Розрахунок електричних і теплових режимів силових рокерних перемикачів та ліній живлення.
 */

/* Питомий опір мідного провідника за 20 °C (Ом·мм²/м) */
#define COPPER_RESISTIVITY_OHM_MM2_M  0.0175

/* Рекомендована максимальна густина струму для мідних ліній (А/мм²) */
#define DEFAULT_MAX_CURRENT_DENSITY   5.0

/**
 * @brief Паспортні електричні та теплові характеристики контактної групи і корпусу рокерного перемикача.
 */
typedef struct {
    double contact_resistance_mohm;  /**< Опір контактної групи (мОм) */
    double rated_current_a;          /**< Номінальний тривалий струм (А) */
    double rated_voltage_v;          /**< Номінальна робоча напруга (В) */
    double thermal_resistance_cw;    /**< Тепловий опір корпус-довкілля R_th (°C/Вт) */
    double max_allowed_temp_c;       /**< Максимально припустима температура корпусу (°C) */
} rocker_switch_t;

/**
 * @brief Параметри провідника силової лінії живлення.
 */
typedef struct {
    double length_m;                 /**< Загальна довжина провідника силової лінії (м) */
    double cross_section_mm2;        /**< Площа поперечного перерізу жили (мм²) */
    double resistivity_ohm_mm2_m;    /**< Питомий опір матеріалу провідника (Ом·мм²/м) */
    double max_current_density_a_mm2;/**< Допустима густина струму (А/мм²) */
} wire_spec_t;

/**
 * @brief Підсумкові результати розрахунку електричних і теплових параметрів силової панелі.
 */
typedef struct {
    double wire_resistance_ohm;      /**< Обчислений опір провідника (Ом) */
    double voltage_drop_v;           /**< Спад напруги на провіднику (В) */
    double voltage_drop_percent;     /**< Відносне падіння напруги (%) */
    double contact_power_loss_w;     /**< Потужність втрат на контактах перемикача (Вт) */
    double wire_power_loss_w;        /**< Джоулеві втрати в провіднику (Вт) */
    double temperature_rise_c;       /**< Перегрів корпусу відносно довкілля (°C) */
    double final_temperature_c;      /**< Підсумкова температура корпусу (°C) */
    double current_density_a_mm2;    /**< Фактична густина струму в провіднику (А/мм²) */
    bool is_thermal_safe;            /**< Прапорець дотримання температурного режиму */
    bool is_voltage_drop_safe;       /**< Прапорець допустимості спаду напруги */
    bool is_current_density_safe;    /**< Прапорець відповідності густини струму */
    bool is_current_rated_safe;      /**< Прапорець недопущення перевищення струму контактів */
} panel_thermal_result_t;

/**
 * @brief Обчислення електричного опору провідника лінії.
 * @param wire Вказівник на специфікацію провідника.
 * @return Опір у Омах, або -1.0 при некоректних вхідних даних.
 */
double calculate_wire_resistance(const wire_spec_t *wire);

/**
 * @brief Розрахунок мінімального необхідного перерізу жили за густиною струму.
 * @param current_a Робочий струм навантаження (А).
 * @param max_density_a_mm2 Максимальна допустима густина струму (А/мм²).
 * @return Мінімальний переріз у мм².
 */
double calculate_minimum_wire_section(double current_a, double max_density_a_mm2);

/**
 * @brief Розрахунок падіння напруги на силовій лінії.
 * @param current_a Струм навантаження (А).
 * @param wire_resistance_ohm Опір провідника (Ом).
 * @return Падіння напруги у Вольтах.
 */
double calculate_voltage_drop(double current_a, double wire_resistance_ohm);

/**
 * @brief Розрахунок потужності втрат на контактах перемикача.
 * @param current_a Струм навантаження (А).
 * @param contact_resistance_mohm Опір контактів (мОм).
 * @return Потужність теплових втрат у Ватах.
 */
double calculate_contact_power_loss(double current_a, double contact_resistance_mohm);

/**
 * @brief Комплексний розрахунок електричного й теплового режиму панелі комутації.
 * @param sw Паспортні дані рокерного перемикача.
 * @param wire Параметри провідника лінії.
 * @param load_current_a Фактичний струм навантаження (А).
 * @param ambient_temp_c Температура навколишнього середовища (°C).
 * @param max_allowed_voltage_drop_percent Допустимий спад напруги (%).
 * @param result Вихідна структура з результатами обчислень.
 * @return true якщо всі критерії безпеки виконуються, false — якщо є порушення.
 */
bool calculate_panel_thermal_result(
    const rocker_switch_t *sw,
    const wire_spec_t *wire,
    double load_current_a,
    double ambient_temp_c,
    double max_allowed_voltage_drop_percent,
    panel_thermal_result_t *result
);

/**
 * @brief Форматований вивід звіту діагностики електричного та теплового стану.
 * @param sw Паспортні дані рокерного перемикача.
 * @param wire Параметри провідника лінії.
 * @param load_current_a Струм навантаження (А).
 * @param ambient_temp_c Температура довкілля (°C).
 * @param result Обчислені результати.
 */
void print_panel_thermal_report(
    const rocker_switch_t *sw,
    const wire_spec_t *wire,
    double load_current_a,
    double ambient_temp_c,
    const panel_thermal_result_t *result
);

#endif /* ROCKER_PANEL_H */
