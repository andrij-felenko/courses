#ifndef PHASE_SELECTOR_H
#define PHASE_SELECTOR_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/** Кількість фаз у трифазній мережі */
#define PHASE_COUNT 3

/** Позначення фаз та відсутності підключення */
typedef enum {
    PHASE_L1 = 0,
    PHASE_L2 = 1,
    PHASE_L3 = 2,
    PHASE_NONE = 0xFF
} phase_id_t;

/** Стани неблокуючого скінченного автомата (FSM) */
typedef enum {
    PHASE_STATE_INIT = 0,      /**< Ініціалізація та відключення всіх контакторів */
    PHASE_STATE_MONITORING,    /**< Моніторинг активної фази та перевірка мережі */
    PHASE_STATE_BREAK_PAUSE,   /**< Захисна бездаркова пауза між розмиканням і замиканням */
    PHASE_STATE_CONNECTING,    /**< Затримка підтвердження стабільності нової фази */
    PHASE_STATE_FAULT          /**< Аварійний стан: жодна фаза не відповідає нормі */
} phase_fsm_state_t;

/** Структура налаштувань порогів напруги та затримок */
typedef struct {
    float v_min_v;             /**< Нижній поріг напруги (В), наприклад 195.0V */
    float v_max_v;             /**< Верхній поріг напруги (В), наприклад 253.0V */
    float v_hysteresis_v;      /**< Гістерезис відпускання/спрацьовування (В), наприклад 5.0V */
    uint32_t break_delay_ms;   /**< Пауза бездаркового розмикання контакторів (мс), наприклад 30 мс */
    uint32_t connect_delay_ms; /**< Затримка підтвердження якості фази перед вмиканням (мс) */
    phase_id_t priority_phase; /**< Пріоритетна фаза (за замовчуванням PHASE_L1) */
} phase_selector_config_t;

/** Тип вказівника на функцію апаратного керування контакторами */
typedef void (*contactor_control_fn)(phase_id_t phase, bool enable);

/** Основний контекст драйвера селектора фаз */
typedef struct {
    phase_selector_config_t config; /**< Конфігурація порогів та затримок */
    float rms_voltage[PHASE_COUNT];  /**< Поточні розраховані значення True RMS (В) */
    bool phase_valid[PHASE_COUNT];   /**< Прапорці відповідності фази допустимому вікну */
    phase_id_t active_phase;         /**< Поточна підключена фаза до навантаження */
    phase_id_t target_phase;         /**< Цільова фаза для наступного підключення */
    phase_fsm_state_t state;         /**< Поточний стан автомата */
    uint32_t state_timer_ms;         /**< Мітка часу/таймер поточного стану (мс) */
    contactor_control_fn set_hardware_contactor; /**< Вказівник на апаратний вихід */
    float adc_v_ref;                 /**< Опорна напруга АЦП (В), наприклад 3.3V */
    uint32_t adc_max_value;          /**< Максимальне значення АЦП (наприклад 4095 для 12 біт) */
    float voltage_divider_ratio;     /**< Коефіцієнт дільника напруги трансформатора/датчика */
} phase_selector_t;

/**
 * @brief Ініціалізація модуля селектора фаз
 */
void phase_selector_init(phase_selector_t *ps,
                         const phase_selector_config_t *config,
                         contactor_control_fn hw_cb,
                         float v_ref,
                         uint32_t adc_max,
                         float divider_ratio);

/**
 * @brief Обчислення True RMS фази за буфером сирих відліків АЦП
 */
void phase_selector_process_adc_buffer(phase_selector_t *ps,
                                         phase_id_t phase,
                                         const uint16_t *adc_samples,
                                         uint32_t sample_count,
                                         uint16_t zero_offset_adc);

/**
 * @brief Основна неблокуюча функція оновлення FSM та логіки перемикання
 */
void phase_selector_process(phase_selector_t *ps, uint32_t current_time_ms);

/**
 * @brief Отримання поточної активної фази
 */
phase_id_t phase_selector_get_active_phase(const phase_selector_t *ps);

/**
 * @brief Перевірка норми напруги конкретної фази
 */
bool phase_selector_is_phase_valid(const phase_selector_t *ps, phase_id_t phase);

#ifdef __cplusplus
}
#endif

#endif /* PHASE_SELECTOR_H */
