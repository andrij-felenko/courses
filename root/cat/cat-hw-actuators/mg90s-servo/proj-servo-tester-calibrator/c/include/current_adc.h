#ifndef CURRENT_ADC_H
#define CURRENT_ADC_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file current_adc.h
 * @brief Модуль струмового моніторингу сервоприводу MG90S V2 на базі АЦП.
 *
 * Дозволяє вимірювати струм споживання через струмовий шунт, застосовувати
 * експоненційне ковзне усереднення (EMA) та розрізняти короткочасний пусковий струм
 * від тривалого заклинювання (stall state) металевого редуктора.
 */

#define ADC_MAX_RAW_VALUE           4095U     /**< 12-бітний АЦП (0 .. 4095) */
#define ADC_VREF_VOLTS              3.3f      /**< Опорна напруга АЦП в вольтах */
#define DEFAULT_SHUNT_RESISTANCE_OHM 0.1f     /**< Опір вимірювального шунта в Омах (0.1 Ом) */

/* Порогові значення струмів для MG90S V2 */
#define INRUSH_CURRENT_THRESHOLD_MA 450.0f    /**< Поріг реєстрації сплеску струму (мА) */
#define STALL_CURRENT_THRESHOLD_MA  750.0f    /**< Критичний поріг струму блокування редуктора (мА) */

#define INRUSH_BLANKING_TIME_MS     120U      /**< Час бланкування пускового струму при старті двигуна (мс) */
#define STALL_CONFIRMATION_TIME_MS  250U      /**< Час утримання струму вище порогу для фіксації заклинювання (мс) */

/**
 * @brief Статус стану струмового моніторингу
 */
typedef enum {
    ADC_STATUS_OK = 0,         /**< Нормальний режим роботи (струм в межах норми) */
    ADC_STATUS_INRUSH,         /**< Короткочасний пусковий сплеск струму (нормальний запуск двигуна) */
    ADC_STATUS_STALL_WARNING,  /**< Перевищення порогу струму, йде відлік часу підтвердження заклинювання */
    ADC_STATUS_STALL_FAULT     /**< КРИТИЧНО: Механічне блокування (stall) редуктора підтверджено! */
} adc_monitor_status_t;

/**
 * @brief Структура вимірювань та фільтрації АЦП
 */
typedef struct {
    uint16_t raw_adc_value;        /**< Останнє значення АЦП (0..4095) */
    float shunt_voltage_mv;        /**< Розрахована напруга на шунті (мВ) */
    float current_ma;              /**< Миттєвий струм споживання (мА) */
    float filtered_current_ma;     /**< Відфільтроване значення струму (мА) */
    
    float filter_alpha;            /**< Коефіцієнт EMA фільтрації (0.0 < alpha <= 1.0) */
    float shunt_resistance_ohm;    /**< Опір шунта в Омах */
    
    adc_monitor_status_t status;   /**< Поточний статус безпеки */
    bool stall_detected;           /**< Прапорець зафіксованого заклинювання редуктора */
    
    uint32_t stall_timer_ms;       /**< Таймер тривалості перевищення струму заклинювання */
    uint32_t inrush_timer_ms;      /**< Таймер бланкування пускового струму */
    uint32_t last_sample_time_ms;  /**< Часова мітка останнього вимірювання (мс) */
} adc_current_monitor_t;

/* Прототипи функцій */

/**
 * @brief Ініціалізує структуру струмового моніторингу АЦП.
 * @param mon Вказівник на структуру моніторингу
 * @param filter_alpha Згладжуючий коефіцієнт EMA (наприклад, 0.2f)
 * @param shunt_ohms Опір вимірювального шунта в Омах (наприклад, 0.1f)
 */
void current_adc_init(adc_current_monitor_t *mon, float filter_alpha, float shunt_ohms);

/**
 * @brief Обробляє новий вибірковий відлік з АЦП та оновлює стан безпеки.
 * @param mon Вказівник на структуру моніторингу
 * @param raw_adc 12-бітове сире значення АЦП
 * @param timestamp_ms Поточний системний час у мілісекундах
 */
void current_adc_process_sample(adc_current_monitor_t *mon, uint16_t raw_adc, uint32_t timestamp_ms);

/**
 * @brief Перевіряє, чи зафіксовано режим аварійного блокування (stall) редуктора.
 * @param mon Вказівник на структуру моніторингу
 * @return true якщо редуктор заклинило, false якщо працює в нормі
 */
bool current_adc_is_stall_detected(const adc_current_monitor_t *mon);

/**
 * @brief Скидає аварійний стан після усунення заклинювання.
 * @param mon Вказівник на структуру моніторингу
 */
void current_adc_reset_fault(adc_current_monitor_t *mon);

#endif /* CURRENT_ADC_H */
