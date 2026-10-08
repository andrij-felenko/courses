/**
 * @file hc_sr505.h
 * @brief Інтерфейс драйвера мініатюрного пасивного інфрачервоного (PIR) давача руху HC-SR505.
 *
 * Модуль реалізує логіку обробки цифрових сигналів від давача HC-SR505, керування
 * силовим N-канальним MOSFET для комутації зовнішнього навантаження та підтримку
 * режимів низького енергоспоживання мікроконтролера.
 */

#ifndef HC_SR505_H
#define HC_SR505_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/** @brief Типовий час утримання активного сигналу HC-SR505 у мілісекундах (апаратний таймаут ~8 с) */
#define HC_SR505_DEFAULT_HOLD_MS     8000U

/** @brief Час стабілізації після вимкнення навантаження перед поверненням у глибокий сон (мс) */
#define HC_SR505_DEFAULT_COOLDOWN_MS 1000U

/**
 * @brief Статуси виконання операцій драйвера HC-SR505.
 */
typedef enum {
    HC_SR505_OK                  =  0, /**< Операція виконана успішно */
    HC_SR505_ERR_NULL_PTR        = -1, /**< Передано вказівник NULL */
    HC_SR505_ERR_INVALID_PARAM   = -2, /**< Некоректні параметри конфігурації */
    HC_SR505_ERR_HAL             = -3, /**< Помилка апаратного рівня (GPIO/EXTI) */
    HC_SR505_ERR_BUSY            = -4  /**< Пристрій зайнятий обробкою іншого стану */
} hc_sr505_status_t;

/**
 * @brief Системні стани машини автоматів драйвера HC-SR505.
 */
typedef enum {
    PIR_STATE_IDLE = 0,         /**< Очікування руху: МК у глибокому сні, MOSFET вимкнено */
    PIR_STATE_MOTION_DETECTED,  /**< Зафіксовано зростаючий фронт (motion active) */
    PIR_STATE_LOAD_ACTIVE,      /**< Навантаження увімкнено через MOSFET, відлік часу активності */
    PIR_STATE_COOLDOWN,         /**< Завершення активності, стабілізація перед сном */
    PIR_STATE_ERROR             /**< Критичний стан помилки */
} pir_state_t;

/**
 * @brief Структура конфігурації драйвера HC-SR505.
 */
typedef struct {
    uint32_t active_hold_ms;    /**< Мінімальний час утримання навантаження увімкненим (мс) */
    uint32_t cooldown_ms;       /**< Затримка стабілізації сенсора після вимкнення навантаження (мс) */
    bool auto_sleep_enable;     /**< Автоматичний перехід МК у режим глибокого сну після обробки */
    bool active_high_logic;     /**< Логічний рівень активного сигналу (true = HIGH, 3.3V) */
} hc_sr505_config_t;

/**
 * @brief Дескриптор екземпляра драйвера HC-SR505.
 */
typedef struct {
    hc_sr505_config_t config;           /**< Налаштування драйвера */
    pir_state_t state;                  /**< Поточний стан системи */
    bool motion_raw_signal;             /**< Поточне значення на цифровому виході OUT */
    bool mosfet_gate_active;            /**< Поточний стан затвора N-канального MOSFET */
    uint32_t motion_trigger_count;      /**< Загальний лічильник виявлених подій руху */
    uint32_t last_trigger_timestamp_ms; /**< Системний час останнього спрацьовування EXTI (мс) */
    uint32_t state_entry_time_ms;       /**< Системний час входу в поточний стан (мс) */
} hc_sr505_t;

/**
 * @brief Ініціалізація драйвера HC-SR505 та первинне конфігурування затвора MOSFET.
 *
 * @param[out] dev    Вказівник на дескриптор пристрою.
 * @param[in]  config Вказівник на конфігураційну структуру.
 * @return HC_SR505_OK у разі успішного завершення, інакше код помилки.
 */
hc_sr505_status_t hc_sr505_init(hc_sr505_t *dev, const hc_sr505_config_t *config);

/**
 * @brief Обробник події зовнішнього переривання (EXTI) від виходу HC-SR505.
 *
 * Функція розрахована на виклик з апаратного ISR при фіксації Rising Edge на GPIO.
 *
 * @param[in,out] dev Вказівник на дескриптор пристрою.
 * @return HC_SR505_OK або код помилки.
 */
hc_sr505_status_t hc_sr505_on_motion_isr(hc_sr505_t *dev);

/**
 * @brief Періодична обробка машини станів HC-SR505 у головному циклі програми.
 *
 * @param[in,out] dev             Вказівник на дескриптор пристрою.
 * @param[in]     current_time_ms Поточний системний час у мілісекундах.
 * @return HC_SR505_OK або код помилки.
 */
hc_sr505_status_t hc_sr505_process(hc_sr505_t *dev, uint32_t current_time_ms);

/**
 * @brief Пряме зчитування поточного логічного рівня з виходу HC-SR505.
 *
 * @param[in,out] dev       Вказівник на дескриптор пристрою.
 * @param[out]    pin_state Змінна для збереження прочитаного стану (true = HIGH, false = LOW).
 * @return HC_SR505_OK або код помилки.
 */
hc_sr505_status_t hc_sr505_read_raw_pin(hc_sr505_t *dev, bool *pin_state);

/**
 * @brief Керування станом затвора N-канального MOSFET.
 *
 * @param[in,out] dev    Вказівник на дескриптор пристрою.
 * @param[in]     enable true — подати V_GS (увімкнути навантаження), false — зняти V_GS.
 * @return HC_SR505_OK або код помилки.
 */
hc_sr505_status_t hc_sr505_set_mosfet(hc_sr505_t *dev, bool enable);

/**
 * @brief Отримання поточного стану машини станів HC-SR505.
 *
 * @param[in] dev Вказівник на дескриптор пристрою.
 * @return Поточний стан pir_state_t.
 */
pir_state_t hc_sr505_get_state(const hc_sr505_t *dev);

/**
 * @brief Перетворення системного стану у текстову термінальну стрічку.
 *
 * @param[in] state Стан драйвера.
 * @return Константний рядок опису стану.
 */
const char* hc_sr505_state_to_str(pir_state_t state);

#ifdef __cplusplus
}
#endif

#endif /* HC_SR505_H */
