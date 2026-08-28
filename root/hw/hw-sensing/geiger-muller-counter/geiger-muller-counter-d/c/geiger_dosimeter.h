/* geiger_dosimeter.h — Драйвер дозиметра на чистому C для вбудованих систем */
#ifndef GEIGER_DOSIMETER_H
#define GEIGER_DOSIMETER_H

#include <stdint.h>
#include <stdbool.h>

#define GEIGER_HISTORY_SECONDS 60   /* Розмір ковзного вікна усереднення */

typedef struct {
    float dead_time_sec;            /* Мертвий час трубки (наприклад 0.000100f для 100 мкс) */
    float cpm_per_usv_h;            /* Коефіцієнт перерахунку (153.8f для СБМ-20) */
    uint32_t min_window_sec;        /* Мінімальне вікно для швидкої реакції */
    uint32_t max_window_sec;        /* Максимальне вікно для фонового режиму */
} geiger_config_t;

typedef struct {
    volatile uint32_t isr_pulse_count;  /* Лічильник переривань */
    uint16_t pulse_history[GEIGER_HISTORY_SECONDS];
    uint32_t history_head;
    uint32_t active_history_len;
    uint32_t total_lifetime_pulses;
    float current_dose_rate_usv_h;
    float current_cpm;
    float statistical_error_percent;
    geiger_config_t config;
} geiger_dosimeter_t;

void geiger_init(geiger_dosimeter_t* dev, const geiger_config_t* cfg);
void geiger_on_pulse_isr(geiger_dosimeter_t* dev);
void geiger_tick_1hz(geiger_dosimeter_t* dev);
float geiger_get_dose_rate(const geiger_dosimeter_t* dev);
float geiger_get_cpm(const geiger_dosimeter_t* dev);
float geiger_get_error_percent(const geiger_dosimeter_t* dev);

#endif /* GEIGER_DOSIMETER_H */

/* geiger_dosimeter.c — Реалізація методів */
#include "geiger_dosimeter.h"
#include <string.h>
#include <math.h>

void geiger_init(geiger_dosimeter_t* dev, const geiger_config_t* cfg) {
    if (!dev || !cfg) return;
    memset(dev, 0, sizeof(geiger_dosimeter_t));
    dev->config = *cfg;
}

void geiger_on_pulse_isr(geiger_dosimeter_t* dev) {
    /* Викликається в обробнику зовнішнього апаратного переривання EXTI */
    dev->isr_pulse_count++;
}

void geiger_tick_1hz(geiger_dosimeter_t* dev) {
    /* Викликається строго один раз на секунду (з системного таймера або RTC) */
    uint32_t current_pulses;

    /* Атомарне зчитування та скидання лічильника переривань */
    current_pulses = dev->isr_pulse_count;
    dev->isr_pulse_count = 0;

    dev->total_lifetime_pulses += current_pulses;

    /* Запис кількості імпульсів за останню секунду в кільцевий буфер */
    dev->pulse_history[dev->history_head] = (uint16_t)current_pulses;
    dev->history_head = (dev->history_head + 1) % GEIGER_HISTORY_SECONDS;

    if (dev->active_history_len < GEIGER_HISTORY_SECONDS) {
        dev->active_history_len++;
    }

    /* Підсумовування імпульсів у активному вікні */
    uint32_t sum_pulses = 0;
    for (uint32_t i = 0; i < dev->active_history_len; i++) {
        sum_pulses += dev->pulse_history[i];
    }

    /* Розрахунок середньої сирої частоти лічби n [1/с] */
    float measured_cps = (float)sum_pulses / (float)dev->active_history_len;

    /* Поправка на мертвий час трубки: N = n / (1 - n * tau) */
    float tau = dev->config.dead_time_sec;
    float dead_time_factor = 1.0f - (measured_cps * tau);

    float corrected_cps = measured_cps;
    if (dead_time_factor > 0.05f) {
        corrected_cps = measured_cps / dead_time_factor;
    } else {
        /* Захист від ділення на нуль при насиченні детектора */
        corrected_cps = measured_cps / 0.05f;
    }

    /* Перерахунок у CPM (відліки за хвилину) та мкЗв/год */
    dev->current_cpm = corrected_cps * 60.0f;
    dev->current_dose_rate_usv_h = dev->current_cpm / dev->config.cpm_per_usv_h;

    /* Статистична невизначеність Пуассона: 1 / sqrt(N) * 100% */
    if (sum_pulses > 0) {
        dev->statistical_error_percent = (1.0f / sqrtf((float)sum_pulses)) * 100.0f;
    } else {
        dev->statistical_error_percent = 100.0f;
    }
}

float geiger_get_dose_rate(const geiger_dosimeter_t* dev) {
    return dev ? dev->current_dose_rate_usv_h : 0.0f;
}

float geiger_get_cpm(const geiger_dosimeter_t* dev) {
    return dev ? dev->current_cpm : 0.0f;
}

float geiger_get_error_percent(const geiger_dosimeter_t* dev) {
    return dev ? dev->statistical_error_percent : 100.0f;
}
