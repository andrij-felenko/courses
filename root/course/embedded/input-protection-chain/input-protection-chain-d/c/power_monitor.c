/* power_monitor.c - Реалізація логіки захисту з гістерезисом */
#include "power_monitor.h"

void PowerMonitor_Init(PowerMonitor_t *mon, const PowerConfig_t *cfg, void (*switch_ctrl)(bool)) {
    if (!mon || !cfg) return;
    mon->config = *cfg;
    mon->state = PWR_STATE_OFF;
    mon->filtered_adc_raw = 0;
    mon->voltage_in_mv = 0;
    mon->fault_counter = 0;
    mon->switch_enabled = false;
    mon->set_switch_fn = switch_ctrl;

    if (mon->set_switch_fn) {
        mon->set_switch_fn(false);
    }
}

void PowerMonitor_ProcessADC(PowerMonitor_t *mon, uint16_t raw_adc) {
    if (!mon) return;

    /* Експоненційний IIR-фільтр низьких частот: y[n] = y[n-1] + (x[n] - y[n-1]) >> shift */
    if (mon->filtered_adc_raw == 0) {
        mon->filtered_adc_raw = (uint32_t)raw_adc << 8;
    } else {
        int32_t diff = (int32_t)((uint32_t)raw_adc << 8) - (int32_t)mon->filtered_adc_raw;
        mon->filtered_adc_raw += (diff >> mon->config.filter_shift);
    }

    uint32_t avg_adc = mon->filtered_adc_raw >> 8;

    /* Перерахунок значення АЦП (12-біт = 4095) у мілівольти вхідної шини */
    uint32_t v_pin_mv = (avg_adc * mon->config.adc_vref_mv) / 4095UL;
    uint32_t div_sum = mon->config.divider_top_k + mon->config.divider_bottom_k;
    mon->voltage_in_mv = (v_pin_mv * div_sum) / mon->config.divider_bottom_k;

    /* Автомат станів захисту з віконним компаратором та гістерезисом */
    switch (mon->state) {
        case PWR_STATE_OFF:
        case PWR_STATE_FAULT_UVLO:
            if (mon->voltage_in_mv >= mon->config.uvlo_recovery_mv &&
                mon->voltage_in_mv <= mon->config.ovlo_recovery_mv) {
                mon->state = PWR_STATE_STARTING;
            }
            break;

        case PWR_STATE_FAULT_OVLO:
            if (mon->voltage_in_mv <= mon->config.ovlo_recovery_mv &&
                mon->voltage_in_mv >= mon->config.uvlo_recovery_mv) {
                mon->state = PWR_STATE_STARTING;
            }
            break;

        case PWR_STATE_STARTING:
            mon->switch_enabled = true;
            if (mon->set_switch_fn) {
                mon->set_switch_fn(true);
            }
            mon->state = PWR_STATE_NORMAL;
            break;

        case PWR_STATE_NORMAL:
            if (mon->voltage_in_mv < mon->config.uvlo_cutoff_mv) {
                /* Миттєве вимикання навантаження при просіданні нижче UVLO */
                mon->switch_enabled = false;
                if (mon->set_switch_fn) mon->set_switch_fn(false);
                mon->state = PWR_STATE_FAULT_UVLO;
                mon->fault_counter++;
            } else if (mon->voltage_in_mv > mon->config.ovlo_cutoff_mv) {
                /* Миттєве вимикання навантаження при стрибку вище OVLO */
                mon->switch_enabled = false;
                if (mon->set_switch_fn) mon->set_switch_fn(false);
                mon->state = PWR_STATE_FAULT_OVLO;
                mon->fault_counter++;
            }
            break;

        case PWR_STATE_FAULT_HARDWARE:
            /* Блокування до скидання або повторної ініціалізації */
            break;
    }
}

void PowerMonitor_HandleHardwareFault(PowerMonitor_t *mon) {
    if (!mon) return;
    mon->switch_enabled = false;
    if (mon->set_switch_fn) {
        mon->set_switch_fn(false);
    }
    mon->state = PWR_STATE_FAULT_HARDWARE;
    mon->fault_counter++;
}

PowerState_t PowerMonitor_GetState(const PowerMonitor_t *mon) {
    return mon ? mon->state : PWR_STATE_FAULT_HARDWARE;
}

uint32_t PowerMonitor_GetVoltageMv(const PowerMonitor_t *mon) {
    return mon ? mon->voltage_in_mv : 0;
}
