#include "battery_guard.h"
#include <stdio.h>

/* Апаратний рівень: зміна логічного рівня піна EN мікросхеми MT3608 */
static void hardware_set_mt3608_en(bool enable) {
    /* На піні EN MT3608:
     * HIGH (> 1.4 В) — перетворювач активний, генерує вихідну напругу;
     * LOW (< 0.4 В) — режим глибокого сну (струм споживання мікросхеми < 1 мкА) */
    if (enable) {
        printf("[GPIO EN] Рівень HIGH: MT3608 увімкнено (активний режим)\n");
    } else {
        printf("[GPIO EN] Рівень LOW: MT3608 ВИМКНЕНО (захист від перерозряду)\n");
    }
}

void battery_guard_init(battery_guard_t *bg, 
                        uint32_t r_top, uint32_t r_bottom, 
                        uint16_t vref_mv, uint16_t adc_max_ticks,
                        uint16_t cutoff_mv, uint16_t recovery_mv) {
    if (!bg) return;

    bg->r_top_ohms = r_top;
    bg->r_bottom_ohms = r_bottom;
    bg->vref_mv = vref_mv;
    bg->adc_max_ticks = adc_max_ticks ? adc_max_ticks : 1023;
    bg->cutoff_voltage_mv = cutoff_mv;
    bg->recovery_voltage_mv = recovery_mv;

    bg->sample_count = 0;
    bg->sample_idx = 0;
    bg->filtered_voltage_mv = 4000; // типовий початковий рівень заряду
    bg->boost_enabled = true;
    bg->status = BATTERY_OK;

    hardware_set_mt3608_en(true);
}

uint16_t battery_guard_raw_to_battery_mv(const battery_guard_t *bg, uint16_t raw_adc) {
    if (!bg || bg->r_bottom_ohms == 0 || bg->adc_max_ticks == 0) return 0;

    /* Розрахунок напруги на піні АЦП у мілівольтах */
    uint32_t v_pin_mv = ((uint32_t)raw_adc * bg->vref_mv) / bg->adc_max_ticks;

    /* Перерахунок через коефіцієнт подільника: Vbat = Vpin * (Rtop + Rbottom) / Rbottom */
    uint32_t v_bat_mv = (v_pin_mv * (bg->r_top_ohms + bg->r_bottom_ohms)) / bg->r_bottom_ohms;
    return (uint16_t)v_bat_mv;
}

void battery_guard_update(battery_guard_t *bg, uint16_t raw_adc) {
    if (!bg) return;

    uint16_t instant_mv = battery_guard_raw_to_battery_mv(bg, raw_adc);

    /* Додавання у кільцевий буфер ковзного середнього */
    bg->history[bg->sample_idx] = instant_mv;
    bg->sample_idx = (bg->sample_idx + 1) % BATTERY_FILTER_SAMPLES;
    if (bg->sample_count < BATTERY_FILTER_SAMPLES) {
        bg->sample_count++;
    }

    uint32_t sum = 0;
    for (uint8_t i = 0; i < bg->sample_count; i++) {
        sum += bg->history[i];
    }
    bg->filtered_voltage_mv = (uint16_t)(sum / bg->sample_count);

    /* Логіка гістерезису захисту */
    if (bg->boost_enabled) {
        if (bg->filtered_voltage_mv <= bg->cutoff_voltage_mv) {
            bg->boost_enabled = false;
            bg->status = BATTERY_CRITICAL_CUTOFF;
            printf("[ЗАХИСТ] Напруга %u мВ <= порогу відсічки %u мВ!\n",
                   bg->filtered_voltage_mv, bg->cutoff_voltage_mv);
            hardware_set_mt3608_en(false);
        } else if (bg->filtered_voltage_mv < bg->recovery_voltage_mv) {
            bg->status = BATTERY_LOW_WARNING;
        } else {
            bg->status = BATTERY_OK;
        }
    } else {
        /* Якщо перетворювач вимкнено, чекаємо підняття напруги вище recovery_voltage */
        if (bg->filtered_voltage_mv >= bg->recovery_voltage_mv) {
            bg->boost_enabled = true;
            bg->status = BATTERY_OK;
            printf("[ВІДНОВЛЕННЯ] Напруга піднялась до %u мВ >= %u мВ. Увімкнення MT3608.\n",
                   bg->filtered_voltage_mv, bg->recovery_voltage_mv);
            hardware_set_mt3608_en(true);
        } else {
            bg->status = BATTERY_CRITICAL_CUTOFF;
        }
    }
}

bool battery_guard_is_boost_enabled(const battery_guard_t *bg) {
    return (bg && bg->boost_enabled);
}

uint16_t battery_guard_get_voltage(const battery_guard_t *bg) {
    return bg ? bg->filtered_voltage_mv : 0;
}
