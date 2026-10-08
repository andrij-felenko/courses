#include "water_flow_sensor.h"
#include <string.h>

/* Внутрішній стан драйвера */
static water_flow_config_t g_config;
static water_flow_metrics_t g_metrics;
static ring_buffer_t g_ring_buf;
static bool g_is_initialized = false;
static uint32_t g_last_calc_timestamp_ms = 0;

/* Симуляція атомарного захисту критичної секції */
static inline void enter_critical_section(void) {
    /* На реальному MCU тут викликається __disable_irq() */
}

static inline void exit_critical_section(void) {
    /* На реальному MCU тут викликається __enable_irq() */
}

bool water_flow_sensor_init(const water_flow_config_t *config) {
    if (config == NULL || config->k_factor <= 0.0f) {
        return false;
    }

    g_config = *config;
    
    ring_buffer_init(&g_ring_buf);

    enter_critical_section();
    g_metrics.pulse_frequency_hz = 0.0f;
    g_metrics.flow_rate_lpm = 0.0f;
    g_metrics.total_volume_liters = 0.0;
    g_metrics.total_pulse_count = 0;
    g_metrics.last_update_ms = 0;
    g_last_calc_timestamp_ms = 0;
    exit_critical_section();

    g_is_initialized = true;
    return true;
}

void water_flow_sensor_on_pulse_isr(uint32_t timestamp_us) {
    if (!g_is_initialized) {
        return;
    }

    ring_buffer_element_t elem = {
        .timestamp_us = timestamp_us,
        .pulse_increment = 1
    };

    /* Додавання події у кільцевий буфер без блокування переривань */
    ring_buffer_push(&g_ring_buf, elem);
}

void water_flow_sensor_process_timer_tick(uint32_t current_timestamp_ms) {
    if (!g_is_initialized) {
        return;
    }

    uint32_t dt_ms = current_timestamp_ms - g_last_calc_timestamp_ms;
    if (dt_ms < g_config.sample_period_ms) {
        return; /* Ще не настав час обчислень */
    }

    g_last_calc_timestamp_ms = current_timestamp_ms;

    /* Вилучення та підрахунок усіх нових імпульсів з кільцевого буфера */
    ring_buffer_element_t elem;
    uint32_t new_pulses_in_period = 0;
    uint32_t latest_timestamp_us = 0;
    uint32_t earliest_timestamp_us = 0xFFFFFFFFU;
    uint32_t popped_count = 0;

    while (ring_buffer_pop(&g_ring_buf, &elem)) {
        new_pulses_in_period += elem.pulse_increment;
        if (elem.timestamp_us < earliest_timestamp_us) {
            earliest_timestamp_us = elem.timestamp_us;
        }
        if (elem.timestamp_us > latest_timestamp_us) {
            latest_timestamp_us = elem.timestamp_us;
        }
        popped_count++;
    }

    float calculated_freq_hz = 0.0f;

    if (popped_count > 0 && latest_timestamp_us > earliest_timestamp_us) {
        float time_delta_sec = (float)(latest_timestamp_us - earliest_timestamp_us) / 1000000.0f;
        if (time_delta_sec > 0.0001f) {
            calculated_freq_hz = (float)new_pulses_in_period / time_delta_sec;
        }
    } else if (popped_count > 0) {
        /* Якщо всі імпульси збіглися у часі, розраховуємо через dt_ms */
        calculated_freq_hz = (float)new_pulses_in_period / ((float)dt_ms / 1000.0f);
    } else {
        /* У разі відсутності нових імпульсів частота дорівнює нулю */
        calculated_freq_hz = 0.0f;
    }

    /* Обчислення миттєвої витрати: Q (л/хв) = f (Гц) / K_factor */
    float calculated_flow_lpm = calculated_freq_hz / g_config.k_factor;

    if (calculated_flow_lpm < g_config.min_flow_cutoff_lpm) {
        calculated_flow_lpm = 0.0f;
        calculated_freq_hz = 0.0f;
    }

    /* Числове інтегрування сумарного об'єму (літри):
     * K_factor визначається як Гц / (л/хв), отже кількість імпульсів на 1 літр = K_factor * 60.0
     */
    double pulses_per_liter = (double)g_config.k_factor * 60.0;
    double added_volume_liters = 0.0;
    if (pulses_per_liter > 0.0) {
        added_volume_liters = (double)new_pulses_in_period / pulses_per_liter;
    }

    /* Атомарне оновлення метрик */
    enter_critical_section();
    g_metrics.pulse_frequency_hz = calculated_freq_hz;
    g_metrics.flow_rate_lpm = calculated_flow_lpm;
    g_metrics.total_volume_liters += added_volume_liters;
    g_metrics.total_pulse_count += new_pulses_in_period;
    g_metrics.last_update_ms = current_timestamp_ms;
    exit_critical_section();
}

void water_flow_sensor_get_metrics(water_flow_metrics_t *out_metrics) {
    if (out_metrics == NULL) {
        return;
    }

    enter_critical_section();
    *out_metrics = g_metrics;
    exit_critical_section();
}

void water_flow_sensor_set_total_volume(double total_liters, uint64_t total_pulses) {
    enter_critical_section();
    g_metrics.total_volume_liters = total_liters;
    g_metrics.total_pulse_count = total_pulses;
    exit_critical_section();
}

ring_buffer_t* water_flow_sensor_get_ring_buffer(void) {
    return &g_ring_buf;
}
