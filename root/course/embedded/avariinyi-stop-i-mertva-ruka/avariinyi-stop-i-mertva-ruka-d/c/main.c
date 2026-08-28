#include <stdint.h>
#include <stdbool.h>

#define PULSE_PERIOD_MS        20U
#define PULSE_DURATION_US      300U
#define DISCREPANCY_MAX_MS     100U
#define EDM_TIMEOUT_MS         250U
#define VIGILANCE_TIMEOUT_MS   30000U
#define VIGILANCE_WARN_MS      3000U

typedef enum {
    SAFETY_STATE_SAFE_DISARMED = 0,
    SAFETY_STATE_ARMED,
    SAFETY_STATE_TRIPPED_ESTOP,
    SAFETY_STATE_TRIPPED_DEADMAN,
    SAFETY_STATE_FAULT_CROSS_CIRCUIT,
    SAFETY_STATE_FAULT_SHORT_POWER,
    SAFETY_STATE_FAULT_DISCORDANCE,
    SAFETY_STATE_FAULT_EDM
} safety_state_t;

typedef enum {
    DEADMAN_POS_RELEASED = 0,
    DEADMAN_POS_ENABLED  = 1,
    DEADMAN_POS_PANIC    = 2
} deadman_pos_t;

typedef struct {
    safety_state_t state;
    bool           output_enable;
    
    /* Таймери та діагностика імпульсів */
    uint32_t       last_tick_ms;
    uint32_t       pulse_timer_ms;
    uint32_t       discrepancy_timer_ms;
    uint32_t       edm_timer_ms;
    uint32_t       vigilance_timer_ms;
    
    bool           ch1_last_raw;
    bool           ch2_last_raw;
    bool           discordance_active;
    
    /* Стан кнопки мертвої руки */
    deadman_pos_t  deadman_state;
    bool           deadman_latched_from_panic;
    bool           vigilance_warning;
} safety_controller_t;

/* Апаратні абстракції платформи */
extern void     hw_set_test_pulse(uint8_t channel, bool level);
extern bool     hw_read_input(uint8_t channel);
extern bool     hw_read_edm_feedback(void);
extern void     hw_set_power_relays(bool enable);
extern void     hw_delay_us(uint32_t us);
extern uint32_t hw_get_time_ms(void);

void safety_controller_init(safety_controller_t *ctrl) {
    ctrl->state = SAFETY_STATE_SAFE_DISARMED;
    ctrl->output_enable = false;
    ctrl->last_tick_ms = hw_get_time_ms();
    ctrl->pulse_timer_ms = 0;
    ctrl->discrepancy_timer_ms = 0;
    ctrl->edm_timer_ms = 0;
    ctrl->vigilance_timer_ms = 0;
    ctrl->ch1_last_raw = false;
    ctrl->ch2_last_raw = false;
    ctrl->discordance_active = false;
    ctrl->deadman_state = DEADMAN_POS_RELEASED;
    ctrl->deadman_latched_from_panic = false;
    ctrl->vigilance_warning = false;
    
    hw_set_test_pulse(1, true);
    hw_set_test_pulse(2, true);
    hw_set_power_relays(false);
}

/* Виконання динамічного тестування каналів зі зсувом фаз */
static bool safety_perform_pulse_test(safety_controller_t *ctrl) {
    /* Канал 1: короткий тестовий провал у нуль */
    hw_set_test_pulse(1, false);
    hw_delay_us(PULSE_DURATION_US);
    bool ch1_during_t1_low = hw_read_input(1);
    bool ch2_during_t1_low = hw_read_input(2);
    hw_set_test_pulse(1, true);
    
    /* Якщо при T1=LOW на вході 1 лишилась одиниця -> КЗ на +24V */
    if (ch1_during_t1_low) {
        ctrl->state = SAFETY_STATE_FAULT_SHORT_POWER;
        return false;
    }
    
    /* Якщо провал на T1 відбився на вході 2 -> міжканальне замикання Ch1-Ch2 */
    if (!ch2_during_t1_low) {
        ctrl->state = SAFETY_STATE_FAULT_CROSS_CIRCUIT;
        return false;
    }
    
    hw_delay_us(100); /* Захисний інтервал між імпульсами */
    
    /* Канал 2: зсунутий тестовий провал у нуль */
    hw_set_test_pulse(2, false);
    hw_delay_us(PULSE_DURATION_US);
    bool ch1_during_t2_low = hw_read_input(1);
    bool ch2_during_t2_low = hw_read_input(2);
    hw_set_test_pulse(2, true);
    
    if (ch2_during_t2_low) {
        ctrl->state = SAFETY_STATE_FAULT_SHORT_POWER;
        return false;
    }
    if (!ch1_during_t2_low) {
        ctrl->state = SAFETY_STATE_FAULT_CROSS_CIRCUIT;
        return false;
    }
    
    return true;
}

void safety_controller_process(safety_controller_t *ctrl, deadman_pos_t raw_deadman, bool reset_cmd) {
    uint32_t now = hw_get_time_ms();
    uint32_t dt = now - ctrl->last_tick_ms;
    ctrl->last_tick_ms = now;
    
    /* Періодичний імпульсний тест лінії */
    ctrl->pulse_timer_ms += dt;
    if (ctrl->pulse_timer_ms >= PULSE_PERIOD_MS) {
        ctrl->pulse_timer_ms = 0;
        if (!safety_perform_pulse_test(ctrl)) {
            hw_set_power_relays(false);
            ctrl->output_enable = false;
            return;
        }
    }
    
    bool ch1 = hw_read_input(1);
    bool ch2 = hw_read_input(2);
    
    /* Контроль розбіжності каналів (Дискорданс) */
    if (ch1 != ch2) {
        if (!ctrl->discordance_active) {
            ctrl->discordance_active = true;
            ctrl->discrepancy_timer_ms = 0;
        } else {
            ctrl->discrepancy_timer_ms += dt;
            if (ctrl->discrepancy_timer_ms > DISCREPANCY_MAX_MS) {
                ctrl->state = SAFETY_STATE_FAULT_DISCORDANCE;
                hw_set_power_relays(false);
                ctrl->output_enable = false;
                return;
            }
        }
    } else {
        ctrl->discordance_active = false;
        ctrl->discrepancy_timer_ms = 0;
    }
    
    bool estop_ok = (ch1 && ch2 && !ctrl->discordance_active);
    
    /* Обробка 3-позиційної мертвої руки */
    if (raw_deadman == DEADMAN_POS_PANIC) {
        ctrl->deadman_latched_from_panic = true;
        ctrl->deadman_state = DEADMAN_POS_PANIC;
    } else if (raw_deadman == DEADMAN_POS_RELEASED) {
        ctrl->deadman_latched_from_panic = false;
        ctrl->deadman_state = DEADMAN_POS_RELEASED;
    } else if (raw_deadman == DEADMAN_POS_ENABLED) {
        if (ctrl->deadman_latched_from_panic) {
            /* Заборонено вмикати при поверненні з Позиції 3 без скидання в Позицію 1 */
            ctrl->deadman_state = DEADMAN_POS_PANIC;
        } else {
            ctrl->deadman_state = DEADMAN_POS_ENABLED;
        }
    }
    
    /* Таймер циклічної пильності */
    if (ctrl->deadman_state == DEADMAN_POS_ENABLED) {
        ctrl->vigilance_timer_ms += dt;
        if (ctrl->vigilance_timer_ms >= VIGILANCE_TIMEOUT_MS) {
            ctrl->state = SAFETY_STATE_TRIPPED_DEADMAN;
            hw_set_power_relays(false);
            ctrl->output_enable = false;
            return;
        } else if (ctrl->vigilance_timer_ms >= (VIGILANCE_TIMEOUT_MS - VIGILANCE_WARN_MS)) {
            ctrl->vigilance_warning = true;
        } else {
            ctrl->vigilance_warning = false;
        }
    } else {
        ctrl->vigilance_timer_ms = 0;
        ctrl->vigilance_warning = false;
    }
    
    /* Кінцевий автомат безпеки */
    switch (ctrl->state) {
        case SAFETY_STATE_SAFE_DISARMED:
        case SAFETY_STATE_TRIPPED_ESTOP:
        case SAFETY_STATE_TRIPPED_DEADMAN:
            if (!estop_ok) {
                ctrl->state = SAFETY_STATE_TRIPPED_ESTOP;
            } else if (ctrl->deadman_state != DEADMAN_POS_ENABLED) {
                ctrl->state = SAFETY_STATE_TRIPPED_DEADMAN;
            } else if (reset_cmd) {
                /* Перевірка зворотного зв'язку контакторів EDM перед пуском */
                if (hw_read_edm_feedback()) {
                    ctrl->state = SAFETY_STATE_ARMED;
                    ctrl->output_enable = true;
                    hw_set_power_relays(true);
                } else {
                    ctrl->state = SAFETY_STATE_FAULT_EDM;
                }
            }
            break;
            
        case SAFETY_STATE_ARMED:
            if (!estop_ok) {
                ctrl->state = SAFETY_STATE_TRIPPED_ESTOP;
                hw_set_power_relays(false);
                ctrl->output_enable = false;
            } else if (ctrl->deadman_state != DEADMAN_POS_ENABLED) {
                ctrl->state = SAFETY_STATE_TRIPPED_DEADMAN;
                hw_set_power_relays(false);
                ctrl->output_enable = false;
            }
            break;
            
        case SAFETY_STATE_FAULT_CROSS_CIRCUIT:
        case SAFETY_STATE_FAULT_SHORT_POWER:
        case SAFETY_STATE_FAULT_DISCORDANCE:
        case SAFETY_STATE_FAULT_EDM:
            /* Фатальні блокування: вимагають виправлення заліза й перезапуску */
            hw_set_power_relays(false);
            ctrl->output_enable = false;
            break;
    }
}
