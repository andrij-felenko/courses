/**
 * @file mems_mcu_hal.h
 * @brief Низькорівневий апаратний інтерфейс (HAL) для керування периферією МК
 *        при роботі з ємнісними MEMS-структурами.
 *
 * Модуль забезпечує абстракцію таймерів протифазного збудження (PWM / GPIO),
 * аналогово-цифрового перетворювача (ADC) для зчитування відгуку мостової схеми
 * та цифро-аналогового перетворювача (DAC) для компенсації початкового зсуву нуля.
 */

#ifndef MEMS_MCU_HAL_H
#define MEMS_MCU_HAL_H

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Коди повернення апаратного рівня HAL.
 */
typedef enum {
    MEMS_HAL_OK = 0,            /**< Операцію виконано успішно */
    MEMS_HAL_ERROR_PARAM = -1,  /**< Некоректні вхідні параметри */
    MEMS_HAL_ERROR_TIMEOUT = -2,/**< Перевищено час очікування готовності периферії */
    MEMS_HAL_ERROR_HW = -3      /**< Апаратна помилка периферійного модуля */
} mems_hal_status_t;

/**
 * @brief Фаза прямокутного сигналу збудження MEMS-структури.
 */
typedef enum {
    MEMS_HAL_PHASE_0 = 0,    /**< Пряма фаза: Excitation_A = HIGH, Excitation_B = LOW */
    MEMS_HAL_PHASE_180 = 1   /**< Інверсна фаза: Excitation_A = LOW, Excitation_B = HIGH */
} mems_hal_phase_t;

/**
 * @brief Структура апаратної конфігурації периферійних модулів МК.
 */
typedef struct {
    uint32_t frequency_hz;       /**< Частота тактування збудження (Гц), наприклад 100000 Гц */
    uint16_t dac_resolution_bits;/**< Розрядність ЦАП (біт), наприклад 12 */
    uint16_t adc_resolution_bits;/**< Розрядність АЦП (біт), наприклад 12 */
    float vref_mv;               /**< Опорна напруга АЦП/ЦАП у мілівольтах (мВ) */
} mems_hal_config_t;

/**
 * @brief Внутрішня структура симуляції фізики MEMS-структури та апаратних регістрів.
 */
typedef struct {
    mems_hal_config_t config;
    mems_hal_phase_t current_phase;
    bool timer_enabled;
    uint16_t dac_raw_value;
    float sim_physical_dC_fF;    /**< Фізичне відхилення ємності dC = C1 - C2 у фемтофарадах */
    float sim_static_offset_fF;  /**< Технологічний стаціонарний зсув асиметрії C1/C2 */
} mems_hal_sim_context_t;

/* Глобальний об'єкт симулятора периферії */
extern mems_hal_sim_context_t g_mems_hal_sim;

/**
 * @brief Ініціалізація ШІМ-таймера та периферійних блоків збудження МК.
 * @param config Вказівник на конфігурацію периферії.
 * @return MEMS_HAL_OK у разі успіху, інакше код помилки.
 */
static inline mems_hal_status_t mems_hal_timer_init(const mems_hal_config_t *config)
{
    if (!config || config->frequency_hz == 0 || config->vref_mv <= 0.0f) {
        return MEMS_HAL_ERROR_PARAM;
    }
    g_mems_hal_sim.config = *config;
    g_mems_hal_sim.current_phase = MEMS_HAL_PHASE_0;
    g_mems_hal_sim.timer_enabled = false;
    g_mems_hal_sim.dac_raw_value = (uint16_t)((1U << config->dac_resolution_bits) / 2U);
    g_mems_hal_sim.sim_physical_dC_fF = 0.0f;
    g_mems_hal_sim.sim_static_offset_fF = 18.5f; /* Технологічна асиметрія 18.5 fF у статиці */
    return MEMS_HAL_OK;
}

/**
 * @brief Перемикання фази прямокутного меандру збудження (0° або 180°).
 * @param phase Цільова фаза сигналу.
 * @return MEMS_HAL_OK у разі успіху.
 */
static inline mems_hal_status_t mems_hal_set_excitation_phase(mems_hal_phase_t phase)
{
    g_mems_hal_sim.current_phase = phase;
    return MEMS_HAL_OK;
}

/**
 * @brief Дозвіл або заборона генерації тактового сигналу збудження.
 * @param enable true — увімкнути генерацію, false — вимкнути.
 * @return MEMS_HAL_OK у разі успіху.
 */
static inline mems_hal_status_t mems_hal_enable_excitation_clk(bool enable)
{
    g_mems_hal_sim.timer_enabled = enable;
    return MEMS_HAL_OK;
}

/**
 * @brief Запис цифрового значення у регістр ЦАП (DAC) для зсуву нульового рівня.
 * @param dac_value Цифровий код ЦАП (0 .. 2^N - 1).
 * @return MEMS_HAL_OK у разі успіху, MEMS_HAL_ERROR_PARAM при перевищенні діапазону.
 */
static inline mems_hal_status_t mems_hal_dac_write_raw(uint16_t dac_value)
{
    uint32_t max_val = (1U << g_mems_hal_sim.config.dac_resolution_bits) - 1U;
    if (dac_value > max_val) {
        return MEMS_HAL_ERROR_PARAM;
    }
    g_mems_hal_sim.dac_raw_value = dac_value;
    return MEMS_HAL_OK;
}

/**
 * @brief Налаштування вихідного рівня ЦАП у мілівольтах.
 * @param voltage_mv Напруга компенсації в мВ.
 * @return MEMS_HAL_OK або код помилки.
 */
static inline mems_hal_status_t mems_hal_dac_set_voltage_mv(float voltage_mv)
{
    if (voltage_mv < 0.0f || voltage_mv > g_mems_hal_sim.config.vref_mv) {
        return MEMS_HAL_ERROR_PARAM;
    }
    uint32_t max_dac = (1U << g_mems_hal_sim.config.dac_resolution_bits) - 1U;
    uint16_t raw = (uint16_t)((voltage_mv / g_mems_hal_sim.config.vref_mv) * (float)max_dac);
    return mems_hal_dac_write_raw(raw);
}

/**
 * @brief Синхронне зчитування вихідної напруги зарядового підсилювача АЦП (ADC).
 *
 * Фізична модель підсилювача відгуку MEMS-структури:
 * V_out = V_bias + K_gain * (dC_total) * Phase_Sign - V_dac_compensation
 * де dC_total = dC_physical + dC_static_offset.
 *
 * @param phase Фаза меандру під час заміру.
 * @param adc_value Вказівник для збереження значення АЦП.
 * @return MEMS_HAL_OK або код помилки.
 */
static inline mems_hal_status_t mems_hal_adc_read_sync_phase(mems_hal_phase_t phase, uint16_t *adc_value)
{
    if (!adc_value) {
        return MEMS_HAL_ERROR_PARAM;
    }

    uint32_t max_adc = (1U << g_mems_hal_sim.config.adc_resolution_bits) - 1U;
    uint32_t max_dac = (1U << g_mems_hal_sim.config.dac_resolution_bits) - 1U;
    float vref = g_mems_hal_sim.config.vref_mv;

    /* Середина шкали АЦП (напруга синфазного зсуву AFE V_cm = Vref / 2) */
    float v_cm = vref / 2.0f;

    /* Сумарне відхилення ємностей dC (фізичне + технологічний зсув) у фемтофарадах */
    float total_dC_fF = g_mems_hal_sim.sim_physical_dC_fF + g_mems_hal_sim.sim_static_offset_fF;

    /* Знак фази збудження: Phase 0° -> +1.0, Phase 180° -> -1.0 */
    float phase_sign = (phase == MEMS_HAL_PHASE_0) ? 1.0f : -1.0f;

    /* Коефіцієнт підсилення зарядового AFE каскаду: 15.0 мВ/fF */
    float afe_gain_mv_per_ff = 15.0f;

    /* Напруга зсуву, що вноситься компенсаційним ЦАП */
    float dac_center_raw = (float)max_dac / 2.0f;
    float dac_offset_mv = ((float)g_mems_hal_sim.dac_raw_value - dac_center_raw) * (vref / (float)max_dac);

    /* Підсумкова аналогова напруга на виході AFE */
    float v_afe_mv = v_cm + (total_dC_fF * afe_gain_mv_per_ff * phase_sign) - dac_offset_mv;

    /* Обмеження діапазоном живлення [0..Vref] */
    if (v_afe_mv < 0.0f) v_afe_mv = 0.0f;
    if (v_afe_mv > vref) v_afe_mv = vref;

    /* Перетворення напруги в цифровий код АЦП */
    uint32_t raw_adc = (uint32_t)((v_afe_mv / vref) * (float)max_adc + 0.5f);
    if (raw_adc > max_adc) raw_adc = max_adc;

    *adc_value = (uint16_t)raw_adc;
    return MEMS_HAL_OK;
}

/**
 * @brief Допоміжна функція симуляції для встановлення механічного зміщення ємності dC.
 * @param dC_fF Фізична зміна ємності внаслідок руху маси MEMS (fF).
 */
static inline void mems_hal_sim_set_displacement(float dC_fF)
{
    g_mems_hal_sim.sim_physical_dC_fF = dC_fF;
}

#ifdef __cplusplus
}
#endif

#endif /* MEMS_MCU_HAL_H */
