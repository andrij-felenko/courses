#include "current_adc.h"
#include <stddef.h>

/**
 * @file current_adc.c
 * @brief Реалізація обробки даних АЦП та алгоритму розрізнення пускових сплесків від блокування.
 */

void current_adc_init(adc_current_monitor_t *mon, float filter_alpha, float shunt_ohms)
{
    if (mon == NULL) {
        return;
    }

    mon->raw_adc_value = 0;
    mon->shunt_voltage_mv = 0.0f;
    mon->current_ma = 0.0f;
    mon->filtered_current_ma = 0.0f;

    /* Обмеження коефіцієнта фільтрації alpha [0.01 .. 1.0] */
    if (filter_alpha <= 0.0f || filter_alpha > 1.0f) {
        mon->filter_alpha = 0.2f;
    } else {
        mon->filter_alpha = filter_alpha;
    }

    if (shunt_ohms <= 0.001f) {
        mon->shunt_resistance_ohm = DEFAULT_SHUNT_RESISTANCE_OHM;
    } else {
        mon->shunt_resistance_ohm = shunt_ohms;
    }

    mon->status = ADC_STATUS_OK;
    mon->stall_detected = false;
    mon->stall_timer_ms = 0;
    mon->inrush_timer_ms = 0;
    mon->last_sample_time_ms = 0;
}

void current_adc_process_sample(adc_current_monitor_t *mon, uint16_t raw_adc, uint32_t timestamp_ms)
{
    if (mon == NULL) {
        return;
    }

    /* 1. Розрахунок інтервалу часу dt між вибірками */
    uint32_t dt_ms = 0;
    if (timestamp_ms >= mon->last_sample_time_ms) {
        dt_ms = timestamp_ms - mon->last_sample_time_ms;
    } else {
        /* Обробка переповнення системного лічильника часу */
        dt_ms = 1U;
    }
    mon->last_sample_time_ms = timestamp_ms;

    /* 2. Обчислення напруги на шунті у мілівольтах:
     * V_shunt = (raw_adc / 4095.0) * VREF_VOLTS * 1000.0 (мВ)
     */
    mon->raw_adc_value = raw_adc;
    mon->shunt_voltage_mv = ((float)raw_adc / (float)ADC_MAX_RAW_VALUE) * (ADC_VREF_VOLTS * 1000.0f);

    /* 3. Перетворення напруги шунта в струм за законом Ома:
     * I (мА) = V_shunt (мВ) / R_shunt (Ом)
     */
    mon->current_ma = mon->shunt_voltage_mv / mon->shunt_resistance_ohm;

    /* 4. Цифрова експоненційна ковзна середня (EMA):
     * I_filtered = alpha * I_instant + (1 - alpha) * I_filtered
     */
    mon->filtered_current_ma = (mon->filter_alpha * mon->current_ma) +
                               ((1.0f - mon->filter_alpha) * mon->filtered_current_ma);

    /* Якщо заклинювання вже підтверджено та зафіксовано, лишаємо фатальний статус до скидання */
    if (mon->stall_detected) {
        mon->status = ADC_STATUS_STALL_FAULT;
        return;
    }

    /* 5. Алгоритм аналізу часових інтервалів для розрізнення пускового струму і блокування редуктора */
    if (mon->filtered_current_ma >= STALL_CURRENT_THRESHOLD_MA) {
        /* Струм перевищує критичний поріг заклинювання */
        mon->stall_timer_ms += dt_ms;

        if (mon->stall_timer_ms >= STALL_CONFIRMATION_TIME_MS) {
            /* Струм утримувався вище порогу дольше часу confirmation - фіксуємо заклинювання */
            mon->status = ADC_STATUS_STALL_FAULT;
            mon->stall_detected = true;
        } else {
            mon->status = ADC_STATUS_STALL_WARNING;
        }
    } else if (mon->filtered_current_ma >= INRUSH_CURRENT_THRESHOLD_MA) {
        /* Струм перевищує поріг запуску, але нижче закритичного заклинювання */
        mon->inrush_timer_ms += dt_ms;

        if (mon->inrush_timer_ms <= INRUSH_BLANKING_TIME_MS) {
            /* Короткочасний пусковий сплеск (Inrush pulse) */
            mon->status = ADC_STATUS_INRUSH;
        } else {
            /* Якщо струм довго не падає, це підвищене навантаження або утримання */
            mon->status = ADC_STATUS_STALL_WARNING;
        }

        /* По поступовому спаданню струму скидаємо таймер заклинювання */
        if (mon->stall_timer_ms > dt_ms) {
            mon->stall_timer_ms -= dt_ms;
        } else {
            mon->stall_timer_ms = 0;
        }
    } else {
        /* Струм у безпечній нормі - плавно скидаємо таймери */
        mon->status = ADC_STATUS_OK;
        mon->stall_timer_ms = 0;
        mon->inrush_timer_ms = 0;
    }
}

bool current_adc_is_stall_detected(const adc_current_monitor_t *mon)
{
    if (mon == NULL) {
        return false;
    }
    return mon->stall_detected;
}

void current_adc_reset_fault(adc_current_monitor_t *mon)
{
    if (mon == NULL) {
        return;
    }

    mon->stall_detected = false;
    mon->status = ADC_STATUS_OK;
    mon->stall_timer_ms = 0;
    mon->inrush_timer_ms = 0;
}
