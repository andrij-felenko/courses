#include <stdint.h>
#include <stdbool.h>

typedef enum {
    MODEM_HW_OFF = 0,
    MODEM_HW_PULSING_PWRKEY,
    MODEM_HW_WAITING_STATUS,
    MODEM_HW_READY,
    MODEM_HW_SLEEP,
    MODEM_HW_RESET_RECOVERY,
    MODEM_HW_FAULT
} modem_hw_state_t;

typedef struct {
    void (*set_pwrkey)(bool low_active);
    void (*set_reset)(bool low_active);
    void (*set_dtr)(bool high_sleep);
    bool (*get_status)(void);
    uint32_t (*get_tick_ms)(void);
} modem_hal_t;

typedef struct {
    modem_hw_state_t state;
    uint32_t timer_start_ms;
    uint32_t pwrkey_pulse_ms;
    uint32_t boot_timeout_ms;
    uint8_t retry_count;
    bool ri_pending_event;
    modem_hal_t hal;
} modem_hw_driver_t;

void modem_hw_init(modem_hw_driver_t *drv, const modem_hal_t *hal) {
    drv->hal = *hal;
    drv->state = MODEM_HW_OFF;
    drv->pwrkey_pulse_ms = 1000;
    drv->boot_timeout_ms = 5000;
    drv->retry_count = 0;
    drv->ri_pending_event = false;

    drv->hal.set_pwrkey(false);
    drv->hal.set_reset(false);
    drv->hal.set_dtr(false);
}

void modem_hw_on_ri_isr(modem_hw_driver_t *drv) {
    drv->ri_pending_event = true;
}

void modem_hw_request_power_on(modem_hw_driver_t *drv) {
    if (drv->state == MODEM_HW_OFF || drv->state == MODEM_HW_FAULT) {
        drv->hal.set_pwrkey(true);
        drv->timer_start_ms = drv->hal.get_tick_ms();
        drv->state = MODEM_HW_PULSING_PWRKEY;
    }
}

void modem_hw_set_sleep(modem_hw_driver_t *drv, bool enable_sleep) {
    if (drv->state == MODEM_HW_READY && enable_sleep) {
        drv->hal.set_dtr(true);
        drv->state = MODEM_HW_SLEEP;
    } else if (drv->state == MODEM_HW_SLEEP && !enable_sleep) {
        drv->hal.set_dtr(false);
        drv->state = MODEM_HW_READY;
    }
}

void modem_hw_poll(modem_hw_driver_t *drv) {
    uint32_t now = drv->hal.get_tick_ms();

    switch (drv->state) {
        case MODEM_HW_PULSING_PWRKEY:
            if (now - drv->timer_start_ms >= drv->pwrkey_pulse_ms) {
                drv->hal.set_pwrkey(false);
                drv->timer_start_ms = now;
                drv->state = MODEM_HW_WAITING_STATUS;
            }
            break;

        case MODEM_HW_WAITING_STATUS:
            if (drv->hal.get_status()) {
                drv->state = MODEM_HW_READY;
                drv->retry_count = 0;
            } else if (now - drv->timer_start_ms >= drv->boot_timeout_ms) {
                if (drv->retry_count++ < 3) {
                    drv->hal.set_reset(true);
                    drv->timer_start_ms = now;
                    drv->state = MODEM_HW_RESET_RECOVERY;
                } else {
                    drv->state = MODEM_HW_FAULT;
                }
            }
            break;

        case MODEM_HW_RESET_RECOVERY:
            if (now - drv->timer_start_ms >= 250) {
                drv->hal.set_reset(false);
                drv->timer_start_ms = now;
                drv->state = MODEM_HW_WAITING_STATUS;
            }
            break;

        case MODEM_HW_SLEEP:
            if (drv->ri_pending_event) {
                drv->ri_pending_event = false;
                modem_hw_set_sleep(drv, false);
            }
            break;

        case MODEM_HW_READY:
        case MODEM_HW_OFF:
        case MODEM_HW_FAULT:
        default:
            break;
    }
}
