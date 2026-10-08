#include "power_monitor.h"
#include <stdio.h>
#include <string.h>

/**
 * @file power_monitor.c
 * @brief Реалізація алгоритмів накопичення енергії та керування сплячим режимом.
 */

/* Глобальні внутрішні контексти модуля */
static ina226_handle_t g_ina226_handle;
static energy_accumulator_t g_accumulator;
static uint32_t g_sample_interval_ms = 1000;
static volatile bool g_timer_flag = false;
static volatile bool g_is_initialized = false;

/* Допоміжні функції імітації критичної секції / блокування переривань */
static inline void enter_critical_section(void) {
    /* На реальному мікроконтролері: __disable_irq() або NVIC_DisableIRQ() */
}

static inline void exit_critical_section(void) {
    /* На реальному мікроконтролері: __enable_irq() або NVIC_EnableIRQ() */
}

ina226_err_t power_monitor_init(const power_monitor_config_t *config)
{
    if (config == NULL || config->sample_interval_ms == 0) {
        return INA226_ERR_INVALID_PARAM;
    }

    g_sample_interval_ms = config->sample_interval_ms;

    /* Ініціалізація давача INA226 */
    ina226_err_t status = ina226_init(&g_ina226_handle, &config->sensor_config);
    if (status != INA226_OK) {
        return status;
    }

    power_monitor_reset_accumulator();
    g_is_initialized = true;
    return INA226_OK;
}

void power_monitor_reset_accumulator(void)
{
    enter_critical_section();
    memset(&g_accumulator, 0, sizeof(energy_accumulator_t));
    exit_critical_section();
}

void power_monitor_process_sample(float delta_time_sec)
{
    if (!g_is_initialized || delta_time_sec <= 0.0f) {
        return;
    }

    ina226_data_t data;
    ina226_err_t status = ina226_read_data(&g_ina226_handle, &data);
    if (status != INA226_OK) {
        return;
    }

    /* 
     * Чисельне інтегрування за методом прямокутників:
     * dt_hours = delta_time_sec / 3600.0
     * dAh = I * dt_hours
     * dWh = P * dt_hours
     */
    double dt_hours = (double)delta_time_sec / 3600.0;
    double d_ah = (double)data.current_a * dt_hours;
    double d_wh = (double)data.power_w * dt_hours;

    enter_critical_section();
    g_accumulator.total_ah += d_ah;
    g_accumulator.total_wh += d_wh;
    g_accumulator.uptime_seconds += (double)delta_time_sec;
    g_accumulator.sample_count++;
    exit_critical_section();
}

void power_monitor_get_accumulator(energy_accumulator_t *out_acc)
{
    if (out_acc == NULL) {
        return;
    }

    /* Атомарна копія для уникнення race condition з ISR */
    enter_critical_section();
    *out_acc = g_accumulator;
    exit_critical_section();
}

ina226_err_t power_monitor_read_instantaneous(ina226_data_t *out_data)
{
    if (!g_is_initialized || out_data == NULL) {
        return INA226_ERR_INVALID_PARAM;
    }
    return ina226_read_data(&g_ina226_handle, out_data);
}

void power_monitor_timer_isr_handler(void)
{
    /* Обробник переривання таймера: фіксує поділ часу та оновлює інтегратор */
    g_timer_flag = true;
    float dt_sec = (float)g_sample_interval_ms / 1000.0f;
    power_monitor_process_sample(dt_sec);
}

void power_monitor_enter_sleep(void)
{
    /* 
     * Перехід мікроконтролера у режим зниженого енергоспоживання (sleep mode).
     * На Cortex-M: __WFI() (Wait For Interrupt).
     * Процесор засинає та пробуджується лише при спрацьовуванні переривання апаратного таймера.
     */
    g_timer_flag = false;
    /* Імітація інструкції WFI на рівні системи */
}
