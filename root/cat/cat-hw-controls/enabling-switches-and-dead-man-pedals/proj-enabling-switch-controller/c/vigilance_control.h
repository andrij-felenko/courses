#ifndef VIGILANCE_CONTROL_H
#define VIGILANCE_CONTROL_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Стани циклу контролю пильності оператора (Vigilance Control).
 */
typedef enum {
    VIGILANCE_OK = 0,         /**< Нормальна робота: оператор проявляє активність */
    VIGILANCE_WARNING,        /**< Попереджувальна фаза: потрібне підтвердження активності */
    VIGILANCE_TRIPPED         /**< Аварійне зупинення: оператор не підтвердив пильність */
} VigilanceState_t;

/**
 * @brief Структура таймера пильності педалі/кнопки (VigilanceTimer_t).
 */
typedef struct {
    uint32_t warning_timeout_ms;    /**< Час до увімкнення попередження */
    uint32_t trip_timeout_ms;       /**< Час від попередження до зупинки */
    uint32_t inactivity_timer;      /**< Лічильник часу нерухомості */
    VigilanceState_t state;         /**< Поточний стан таймера */
    bool warning_buzzer;            /**< Прапор увімкнення звукового сигналу */
    bool warning_lamp;              /**< Прапор увімкнення світлового сигналу */
} VigilanceTimer_t;

/**
 * @brief Ініціалізація модулю контролю пильності.
 */
void VigilanceControl_Init(VigilanceTimer_t *vt, uint32_t warning_ms, uint32_t trip_ms);

/**
 * @brief Скидання таймера нерухомості (при натисканні/відпусканні або події пильності).
 */
void VigilanceControl_Reset(VigilanceTimer_t *vt);

/**
 * @brief Оновлення таймера пильності.
 * @param vt Вказівник на структуру.
 * @param is_enabled Прапор перебування пристрою дозволу в стані ENABLE.
 * @param delta_ms Інтервал часу в мілісекундах.
 * @return Поточний стан контролю пильності.
 */
VigilanceState_t VigilanceControl_Update(VigilanceTimer_t *vt, bool is_enabled, uint32_t delta_ms);

#endif // VIGILANCE_CONTROL_H
