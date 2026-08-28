/* thermal_compensator.h - C99 референтна реалізація */
#ifndef THERMAL_COMPENSATOR_H
#define THERMAL_COMPENSATOR_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Параметри теплової моделі плати (визначаються під час калібрування)
 */
typedef struct {
    float r_th1;        /* Тепловий опір 1-ї ланки (корпус чіпа), К/Вт */
    float tau1;         /* Постійна часу 1-ї ланки, секунди */
    float r_th2;        /* Тепловий опір 2-ї ланки (масив плати), К/Вт */
    float tau2;         /* Постійна часу 2-ї ланки, секунди */
    float p_quiescent;  /* Базове статичне споживання плати у спокої, Вт */
    float p_wifi_tx;    /* Теплова потужність радіопередавача під час TX, Вт */
    float p_cpu_active; /* Додаткове тепловиділення CPU при 100% завантаженні, Вт */
} thermal_config_t;

/**
 * @brief Стан та контекст теплового фільтра
 */
typedef struct {
    thermal_config_t cfg;
    float dt;           /* Період дискретизації оновлення фільтра, секунди */
    float alpha1;       /* Коефіцієнт експоненційного згладжування 1-ї ланки */
    float alpha2;       /* Коефіцієнт експоненційного згладжування 2-ї ланки */
    float state_t1;     /* Поточний перегрів 1-ї ланки, °C */
    float state_t2;     /* Поточний перегрів 2-ї ланки, °C */
    bool initialized;   /* Прапорець успішної ініціалізації */
} thermal_filter_t;

/**
 * @brief Ініціалізація компенсатора та розрахунок коефіцієнтів
 * @param filter Вказівник на екземпляр структури фільтра
 * @param cfg Вказівник на конфігурацію калібрувальних параметрів
 * @param dt_seconds Період опитування в секундах (наприклад, 1.0f для 1 Гц)
 */
void thermal_filter_init(thermal_filter_t *filter, const thermal_config_t *cfg, float dt_seconds);

/**
 * @brief Скидання накопиченого тепла (застосовується при холодному старті)
 */
void thermal_filter_reset(thermal_filter_t *filter);

/**
 * @brief Встановлення початкового теплового стану (наприклад, після теплого перезавантаження)
 * @param filter Вказівник на фільтр
 * @param initial_self_heat Початкова оцінка перегріву плати, °C
 */
void thermal_filter_set_state(thermal_filter_t *filter, float initial_self_heat);

/**
 * @brief Основна функція оновлення фільтра та розрахунку компенсації
 * @param filter Вказівник на екземпляр фільтра
 * @param t_raw_celsius Необроблене вимірювання термодавача, °C
 * @param cpu_load Відносне завантаження процесора (0.0f - 1.0f)
 * @param tx_duty_cycle Частка активності радіопередавача (0.0f - 1.0f)
 * @return Відновлена температура навколишнього середовища, °C
 */
float thermal_filter_update(thermal_filter_t *filter, float t_raw_celsius,
                            float cpu_load, float tx_duty_cycle);

/**
 * @brief Отримання поточної змодельованої поправки перегріву
 */
float thermal_filter_get_delta(const thermal_filter_t *filter);

#ifdef __cplusplus
}
#endif

#endif /* THERMAL_COMPENSATOR_H */

/* thermal_compensator.c */
#include "thermal_compensator.h"
#include <math.h>

void thermal_filter_init(thermal_filter_t *filter, const thermal_config_t *cfg, float dt_seconds) {
    if (!filter || !cfg || dt_seconds <= 0.0f) {
        return;
    }
    filter->cfg = *cfg;
    filter->dt = dt_seconds;

    /* Розрахунок дискретних коефіцієнтів фільтра першого порядку:
     * alpha = exp(-dt / tau). При малих dt/tau це еквівалентно 1 - dt/tau */
    filter->alpha1 = (cfg->tau1 > 0.0f) ? expf(-dt_seconds / cfg->tau1) : 0.0f;
    filter->alpha2 = (cfg->tau2 > 0.0f) ? expf(-dt_seconds / cfg->tau2) : 0.0f;

    filter->state_t1 = 0.0f;
    filter->state_t2 = 0.0f;
    filter->initialized = true;
}

void thermal_filter_reset(thermal_filter_t *filter) {
    if (!filter) return;
    filter->state_t1 = 0.0f;
    filter->state_t2 = 0.0f;
}

void thermal_filter_set_state(thermal_filter_t *filter, float initial_self_heat) {
    if (!filter) return;
    /* Розподіляємо початковий перегрів пропорційно тепловим опорам ланок */
    float r_total = filter->cfg.r_th1 + filter->cfg.r_th2;
    if (r_total > 0.0f) {
        filter->state_t1 = initial_self_heat * (filter->cfg.r_th1 / r_total);
        filter->state_t2 = initial_self_heat * (filter->cfg.r_th2 / r_total);
    } else {
        filter->state_t1 = 0.0f;
        filter->state_t2 = initial_self_heat;
    }
}

float thermal_filter_update(thermal_filter_t *filter, float t_raw_celsius,
                            float cpu_load, float tx_duty_cycle) {
    if (!filter || !filter->initialized) {
        return t_raw_celsius;
    }

    /* Захисне насичення вхідних коефіцієнтів у діапазоні від 0.0 до 1.0 */
    if (cpu_load < 0.0f) cpu_load = 0.0f;
    if (cpu_load > 1.0f) cpu_load = 1.0f;
    if (tx_duty_cycle < 0.0f) tx_duty_cycle = 0.0f;
    if (tx_duty_cycle > 1.0f) tx_duty_cycle = 1.0f;

    /* 1. Розрахунок поточної теплової потужності активних вузлів */
    float p_total = filter->cfg.p_quiescent +
                    (filter->cfg.p_cpu_active * cpu_load) +
                    (filter->cfg.p_wifi_tx * tx_duty_cycle);

    /* 2. Чисельне інтегрування 1-ї ланки (кристал та корпус чіпа) */
    float target_t1 = filter->cfg.r_th1 * p_total;
    filter->state_t1 = (filter->alpha1 * filter->state_t1) +
                       ((1.0f - filter->alpha1) * target_t1);

    /* 3. Чисельне інтегрування 2-ї ланки (масив друкованої плати) */
    float target_t2 = filter->cfg.r_th2 * p_total;
    filter->state_t2 = (filter->alpha2 * filter->state_t2) +
                       ((1.0f - filter->alpha2) * target_t2);

    /* 4. Сумарна паразитна температурна добавка */
    float delta_t_self = filter->state_t1 + filter->state_t2;

    /* 5. Відновлення істинної температури середовища */
    return t_raw_celsius - delta_t_self;
}

float thermal_filter_get_delta(const thermal_filter_t *filter) {
    if (!filter) return 0.0f;
    return filter->state_t1 + filter->state_t2;
}
