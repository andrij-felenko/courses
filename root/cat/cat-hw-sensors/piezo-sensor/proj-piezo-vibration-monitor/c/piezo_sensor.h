#ifndef PIEZO_SENSOR_H
#define PIEZO_SENSOR_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Параметри конфігурації цифрового фільтра та порогового компаратора.
 */
typedef struct {
    uint16_t baseline_adc;          /**< Базовий нульовий рівень АЦП (напр., 2048 для 12-біт АЦП) */
    float attack_factor;            /**< Коефіцієнт наростання огинаючої (0.0f..1.0f) */
    float decay_factor;             /**< Коефіцієнт згасання огинаючої (0.0f..1.0f) */
    float energy_alpha;             /**< Коефіцієнт експоненційного згладжування оцінки енергії */
    float alarm_threshold_high;     /**< Верхній поріг спрацьовування сигналу тривоги */
    float alarm_threshold_low;      /**< Нижній поріг скидання тривоги (гістерезис) */
} piezo_config_t;

/**
 * @brief Структурний дескриптор стану п'єзоелектричного давача.
 */
typedef struct {
    piezo_config_t config;          /**< Конфігураційні параметри */
    float envelope;                 /**< Поточне розраховане значення огинаючої сигналу */
    float energy;                   /**< Поточна оцінка накопиченої енергії вібраційного впливу */
    uint32_t peak_count;            /**< Загальна кількість зафіксованих механічних ударів */
    bool alarm_active;              /**< Поточний стан тривоги (true — аномальна вібрація) */
} piezo_sensor_t;

/**
 * @brief Ініціалізація модуля обробки даних п'єзоелектричного давача.
 *
 * @param sensor Вказівник на екземпляр давача.
 * @param config Вказівник на структуру конфігурації.
 * @return true — ініціалізацію виконано успішно, false — помилка параметрів.
 */
bool piezo_sensor_init(piezo_sensor_t *sensor, const piezo_config_t *config);

/**
 * @brief Обробка нового відліку АЦП (цифрова обробка сигналу в реальному часі).
 *
 * @param sensor Вказівник на екземпляр давача.
 * @param adc_raw Сирий відлік аналогово-цифрового перетворювача.
 */
void piezo_sensor_process_sample(piezo_sensor_t *sensor, uint16_t adc_raw);

/**
 * @brief Скидання накопиченого стану огинаючої, енергії та тривоги.
 *
 * @param sensor Вказівник на екземпляр давача.
 */
void piezo_sensor_reset(piezo_sensor_t *sensor);

/**
 * @brief Зчитування поточного значення огинаючої сигналу.
 *
 * @param sensor Вказівник на екземпляр давача.
 * @return Значення огинаючої вібрацій.
 */
float piezo_sensor_get_envelope(const piezo_sensor_t *sensor);

/**
 * @brief Зчитування поточної оцінки енергії вібраційного впливу.
 *
 * @param sensor Вказівник на екземпляр давача.
 * @return Оцінка енергії вібрації.
 */
float piezo_sensor_get_energy(const piezo_sensor_t *sensor);

/**
 * @brief Перевірка активності сигналу тривоги.
 *
 * @param sensor Вказівник на екземпляр давача.
 * @return true — тривога активна, false — режим норми.
 */
bool piezo_sensor_is_alarm_active(const piezo_sensor_t *sensor);

#endif /* PIEZO_SENSOR_H */
