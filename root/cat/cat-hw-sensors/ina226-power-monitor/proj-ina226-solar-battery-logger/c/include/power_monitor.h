#ifndef POWER_MONITOR_H
#define POWER_MONITOR_H

#include "ina226.h"
#include <stdint.h>
#include <stdbool.h>

/**
 * @file power_monitor.h
 * @brief Оголошення модуля чисельного інтегрування енергії та енергоефективного керування MCU.
 *
 * Модуль виконує розрахунок накопиченого енергоспоживання (А·год, Вт·год)
 * за методом прямокутників, забезпечує атомарне зчитування підсумків з обробника
 * переривань апаратного таймера та керує режимом сплячки (Sleep Mode) мікроконтролера.
 */

/**
 * @brief Структурний акумулятор накопиченої енергії.
 */
typedef struct {
    double total_ah;        /**< Накопичена ємність в Ампер-годинах (А·год) */
    double total_wh;        /**< Накопичена енергія у Ват-годинах (Вт·год) */
    double uptime_seconds;  /**< Загальний час вимірювання у секундах (с) */
    uint64_t sample_count;  /**< Кількість обчислених циклів вимірювання */
} energy_accumulator_t;

/**
 * @brief Конфігурація модуля моніторингу живлення.
 */
typedef struct {
    ina226_config_t sensor_config; /**< Первинні налаштування давача INA226 */
    uint32_t sample_interval_ms;   /**< Період вимірювання апаратного таймера (мс) */
} power_monitor_config_t;

/* --- Прототипи функцій модуля power_monitor --- */

/**
 * @brief Ініціалізація модуля моніторингу живлення та давача INA226.
 * @param config Налаштування системи та таймера.
 * @return INA226_OK у разі успіху.
 */
ina226_err_t power_monitor_init(const power_monitor_config_t *config);

/**
 * @brief Крок чисельного інтегрування струму й потужності за інтервал dt.
 * @param delta_time_sec Тривалість інтервалу дискретизації у секундах.
 */
void power_monitor_process_sample(float delta_time_sec);

/**
 * @brief Атомарне зчитування накопиченої енергії з акумулятора.
 * @param out_acc Указівник на структуру для збереження копії акумулятора.
 */
void power_monitor_get_accumulator(energy_accumulator_t *out_acc);

/**
 * @brief Скинути лічильники накопиченої енергії у нуль.
 */
void power_monitor_reset_accumulator(void);

/**
 * @brief Зчитати миттєві виміряні параметри з давача INA226.
 * @param out_data Указівник на структуру з показниками.
 * @return INA226_OK у разі успіху.
 */
ina226_err_t power_monitor_read_instantaneous(ina226_data_t *out_data);

/**
 * @brief Обробник переривання апаратного таймера (ISR).
 * 
 * Викликається періодично таймером для зчитування давача та інтегрування показань.
 */
void power_monitor_timer_isr_handler(void);

/**
 * @brief Перевести мікроконтролер у режим зниженого енергоспоживання (Sleep Mode).
 * 
 * Зупиняє процесор до наступного пробудження від апаратного таймера.
 */
void power_monitor_enter_sleep(void);

#endif /* POWER_MONITOR_H */
