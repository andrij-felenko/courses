#ifndef PHASE_SELECTOR_H
#define PHASE_SELECTOR_H

#include <stdint.h>
#include <stdbool.h>
#include "esp_err.h"
#include "driver/gpio.h"
#include "driver/adc.h"

#ifdef __cplusplus
extern "C" {
#endif

/// Ідентифікатор трифазної мережі
typedef enum {
    PHASE_NONE = 0, ///< Жодна фаза не підключена
    PHASE_L1   = 1, ///< Перша фаза (L1, пріоритетна)
    PHASE_L2   = 2, ///< Друга фаза (L2, резерв 1)
    PHASE_L3   = 3  ///< Третя фаза (L3, резерв 2)
} phase_id_t;

/// Стани скінченного автомата (FSM) перемикача
typedef enum {
    FSM_STATE_INIT = 0,         ///< Ініціалізація та первинне очікування
    FSM_STATE_MONITOR,          ///< Моніторинг та утримання поточного стану
    FSM_STATE_DEAD_TIME,        ///< Пауза гасіння дуги (міжфазний dead-time)
    FSM_STATE_RETURN_DELAY,     ///< Затримка повернення на пріоритетну фазу
    FSM_STATE_FAULT             ///< Аварійний стан (відсутність нормованих фаз)
} phase_selector_fsm_t;

/**
 * @brief Структура конфігурації межевих уставок напруги, гістерезису та часових інтервалів
 */
typedef struct {
    adc1_channel_t adc_channel_l1;  ///< Канал АЦП для вимірювання фази L1
    adc1_channel_t adc_channel_l2;  ///< Канал АЦП для вимірювання фази L2
    adc1_channel_t adc_channel_l3;  ///< Канал АЦП для вимірювання фази L3
    gpio_num_t relay_gpio_l1;       ///< GPIO керування силовим реле фази L1
    gpio_num_t relay_gpio_l2;       ///< GPIO керування силовим реле фази L2
    gpio_num_t relay_gpio_l3;       ///< GPIO керування силовим реле фази L3
    float v_min_threshold;          ///< Нижня межа напруги True-RMS (В), наприклад 180.0
    float v_max_threshold;          ///< Верхня межа напруги True-RMS (В), наприклад 250.0
    float v_hysteresis;             ///< Ширина зони гістерезису (В), наприклад 5.0
    uint32_t t_transfer_ms;         ///< Затримка гасіння дуги (dead-time) у мс
    uint32_t t_return_ms;           ///< Затримка повернення на пріоритетну фазу у мс
    phase_id_t priority_phase;      ///< Пріоритетна фаза (зазвичай PHASE_L1)
} phase_selector_config_t;

/**
 * @brief Структура поточного стану контролера, вибору активної фази та лічильників
 */
typedef struct {
    float v_rms_l1;                 ///< Обчислене значення True-RMS для фази L1 (В)
    float v_rms_l2;                 ///< Обчислене значення True-RMS для фази L2 (В)
    float v_rms_l3;                 ///< Обчислене значення True-RMS для фази L3 (В)
    phase_id_t active_phase;        ///< Поточно підключена силова фаза
    phase_id_t target_phase;        ///< Цільова фаза для переключення
    phase_selector_fsm_t fsm_state; ///< Поточний стан автомата FSM
    bool is_valid_l1;               ///< Статус відповідності нормі фази L1
    bool is_valid_l2;               ///< Статус відповідності нормі фази L2
    bool is_valid_l3;               ///< Статус відповідності нормі фази L3
} phase_selector_status_t;

/**
 * @brief Ініціалізація периферії АЦП, GPIO та параметрів перемикача фаз
 * @param config Вказівник на структуру конфігурації
 * @return ESP_OK у разі успішного налаштування
 */
esp_err_t phase_selector_init(const phase_selector_config_t *config);

/**
 * @brief Передача масиву вибірок мгновеної напруги для обчислення True-RMS
 * @param samples_l1 Масив вибірок фази L1
 * @param samples_l2 Масив вибірок фази L2
 * @param samples_l3 Масив вибірок фази L3
 * @param num_samples Кількість вибірок у масивах
 * @return ESP_OK після виконання розрахунку
 */
esp_err_t phase_selector_process_samples(const float samples_l1[], 
                                         const float samples_l2[], 
                                         const float samples_l3[], 
                                         uint32_t num_samples);

/**
 * @brief Оновлення стану автомата FSM та неблокувальне керування реле
 * @param out_status Вказівник на структуру для повернення результатів
 * @return ESP_OK при успішному виконанні ітерації
 */
esp_err_t phase_selector_update(phase_selector_status_t *out_status);

#ifdef __cplusplus
}
#endif

#endif // PHASE_SELECTOR_H
