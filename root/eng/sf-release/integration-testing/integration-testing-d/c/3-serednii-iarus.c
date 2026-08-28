#include <stdint.h>
#include <stdbool.h>

#define I2C_BUS_RECOVERY_PULSES   9
#define I2C_TIMEOUT_MAX_TICKS     1000

typedef enum {
    I2C_STATE_IDLE = 0,
    I2C_STATE_BUSY,
    I2C_STATE_TIMEOUT,
    I2C_STATE_RECOVERING,
    I2C_STATE_ERROR
} i2c_bus_state_t;

typedef struct {
    i2c_bus_state_t state;
    uint32_t wait_ticks;
    uint8_t recovery_pulse_count;
    bool sda_stuck_low;
} i2c_recovery_fsm_t;

void i2c_recovery_init(i2c_recovery_fsm_t *fsm) {
    if (!fsm) return;
    fsm->state = I2C_STATE_IDLE;
    fsm->wait_ticks = 0;
    fsm->recovery_pulse_count = 0;
    fsm->sda_stuck_low = false;
}

void i2c_recovery_tick(i2c_recovery_fsm_t *fsm, bool sda_pin_state, bool scl_pin_state) {
    if (!fsm) return;

    switch (fsm->state) {
    case I2C_STATE_IDLE:
        fsm->wait_ticks = 0;
        break;

    case I2C_STATE_BUSY:
        fsm->wait_ticks++;
        if (fsm->wait_ticks > I2C_TIMEOUT_MAX_TICKS) {
            fsm->state = I2C_STATE_TIMEOUT;
        }
        break;

    case I2C_STATE_TIMEOUT:
        if (!sda_pin_state) {
            fsm->sda_stuck_low = true;
            fsm->recovery_pulse_count = 0;
            fsm->state = I2C_STATE_RECOVERING;
        } else {
            fsm->state = I2C_STATE_ERROR;
        }
        break;

    case I2C_STATE_RECOVERING:
        if (fsm->recovery_pulse_count < I2C_BUS_RECOVERY_PULSES) {
            fsm->recovery_pulse_count++;
            if (sda_pin_state) {
                fsm->sda_stuck_low = false;
                fsm->state = I2C_STATE_IDLE;
            }
        } else {
            fsm->state = sda_pin_state ? I2C_STATE_IDLE : I2C_STATE_ERROR;
        }
        break;

    case I2C_STATE_ERROR:
        break;
    }
}
