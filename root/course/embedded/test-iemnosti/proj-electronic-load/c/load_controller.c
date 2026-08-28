/* load_controller.c */
#include "load_controller.h"
#include <stdio.h>

static const load_hal_t *s_hal = NULL;

void load_tester_init(load_tester_t *t, const load_config_t *cfg, const load_hal_t *hal) {
    if (!t || !cfg || !hal) return;
    s_hal = hal;
    t->cfg = *cfg;
    t->state = STATE_IDLE;
    t->v_cell_mv = 0;
    t->i_actual_ma = 0;
    t->temp_heatsink_c = 0;
    t->microamp_seconds = 0;
    t->microwatt_seconds = 0;
    t->last_dc_ir_mohm = 0;
    t->ir_timer_ms = 0;
    t->elapsed_ms = 0;
    
    if (s_hal->set_dac_current_ma) {
        s_hal->set_dac_current_ma(0);
    }
}

void load_tester_start(load_tester_t *t) {
    if (!t) return;
    t->state = STATE_RUNNING;
    t->microamp_seconds = 0;
    t->microwatt_seconds = 0;
    t->elapsed_ms = 0;
    t->ir_timer_ms = 0;
}

void load_tester_stop(load_tester_t *t) {
    if (!t) return;
    t->state = STATE_IDLE;
    if (s_hal && s_hal->set_dac_current_ma) {
        s_hal->set_dac_current_ma(0);
    }
}

static uint32_t compute_target_current_ma(load_tester_t *t) {
    switch (t->cfg.mode) {
        case MODE_CC:
            return t->cfg.setpoint_val;
            
        case MODE_CR:
            /* I = V / R; V в мВ, R в мОм -> I = (V * 1000) / R */
            if (t->cfg.setpoint_val == 0) return 0;
            return (t->v_cell_mv * 1000UL) / t->cfg.setpoint_val;
            
        case MODE_CP:
            /* I = P / V; P в мВт, V в мВ -> I = (P * 1000) / V */
            if (t->v_cell_mv < 500) return 0; /* Захист від ділення на нуль */
            return (t->cfg.setpoint_val * 1000UL) / t->v_cell_mv;
            
        case MODE_PULSED: {
            uint32_t phase = t->elapsed_ms % t->cfg.pulse_period_ms;
            if (phase < t->cfg.pulse_high_ms) {
                return t->cfg.pulse_high_ma;
            } else {
                return t->cfg.pulse_low_ma;
            }
        }
        default:
            return 0;
    }
}

void load_tester_tick(load_tester_t *t, uint32_t dt_ms) {
    if (!t || !s_hal) return;

    /* 1. Зчитування фізичних сигналів АЦП (4-провідні виміри) */
    s_hal->read_adc_channels(&t->v_cell_mv, &t->i_actual_ma, &t->temp_heatsink_c);
    
    if (t->state != STATE_RUNNING && t->state != STATE_IR_STEP) {
        s_hal->set_dac_current_ma(0);
        return;
    }

    /* 2. Захисти: Термічний та Відсічка за напругою */
    if (t->temp_heatsink_c >= t->cfg.max_temp_c) {
        s_hal->set_dac_current_ma(0);
        t->state = STATE_OVERHEAT_FAULT;
        return;
    }

    if (t->v_cell_mv <= t->cfg.cutoff_mv && t->v_cell_mv > 200) {
        s_hal->set_dac_current_ma(0);
        t->state = STATE_CUTOFF_REACHED;
        return;
    }

    /* 3. Періодичний вимір DC IR (кожні 30 секунд: імпульсний стрибок 100 мс) */
    t->ir_timer_ms += dt_ms;
    if (t->state == STATE_RUNNING && t->ir_timer_ms >= 30000) {
        t->state = STATE_IR_STEP;
        t->ir_v_baseline_mv = t->v_cell_mv;
        t->ir_i_baseline_ma = t->i_actual_ma;
        
        /* Ступінчасте збільшення струму на +200 мА */
        s_hal->set_dac_current_ma(t->i_actual_ma + 200);
        return;
    }

    if (t->state == STATE_IR_STEP) {
        if (t->ir_timer_ms >= 30100) { /* Минуло 100 мс після сходинки */
            int32_t delta_v = (int32_t)t->ir_v_baseline_mv - (int32_t)t->v_cell_mv;
            int32_t delta_i = (int32_t)t->i_actual_ma - (int32_t)t->ir_i_baseline_ma;
            
            if (delta_i > 50 && delta_v > 0) {
                /* R_dc = (ΔV_mV * 1000) / ΔI_mA -> в мОм */
                t->last_dc_ir_mohm = (uint32_t)((delta_v * 1000L) / delta_i);
            }
            t->ir_timer_ms = 0;
            t->state = STATE_RUNNING;
        } else {
            return; /* Утримуємо імпульс 100 мс */
        }
    }

    /* 4. Керування струмом навантаження */
    uint32_t target_i_ma = compute_target_current_ma(t);
    s_hal->set_dac_current_ma(target_i_ma);

    /* 5. Чисельне інтегрування енергії та ємності */
    t->microamp_seconds += (uint64_t)t->i_actual_ma * 1000ULL * dt_ms / 1000ULL;
    uint32_t power_mw = (uint32_t)(((uint64_t)t->v_cell_mv * t->i_actual_ma) / 1000ULL);
    t->microwatt_seconds += (uint64_t)power_mw * 1000ULL * dt_ms / 1000ULL;

    t->elapsed_ms += dt_ms;

    /* 6. Логування в CSV форматі раз на секунду */
    if (t->elapsed_ms % 1000 < dt_ms) {
        char buf[128];
        uint32_t mah = (uint32_t)(t->microamp_seconds / 3600000ULL);
        uint32_t mwh = (uint32_t)(t->microwatt_seconds / 3600000ULL);
        snprintf(buf, sizeof(buf), "%lu,%lu,%lu,%lu,%lu,%lu\r\n",
                 (unsigned long)t->elapsed_ms / 1000,
                 (unsigned long)t->v_cell_mv,
                 (unsigned long)t->i_actual_ma,
                 (unsigned long)mah,
                 (unsigned long)mwh,
                 (unsigned long)t->last_dc_ir_mohm);
        if (s_hal->send_uart_log) {
            s_hal->send_uart_log(buf);
        }
    }
}
