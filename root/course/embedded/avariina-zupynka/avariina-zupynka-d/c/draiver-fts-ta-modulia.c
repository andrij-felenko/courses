#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define FTS_MAGIC_BYTE           0x5AU
#define FTS_CMD_KILL_POWER       0xA5U
#define FTS_CMD_ARM_SYSTEM       0x5AU
#define FTS_HEARTBEAT_TIMEOUT_MS 500U
#define PARACHUTE_DELAY_MS       80U

typedef enum {
    PLATFORM_MULTICOPTER = 0,
    PLATFORM_FIXED_WING,
    PLATFORM_ROVER
} platform_type_t;

typedef enum {
    FTS_STATE_DISARMED = 0,
    FTS_STATE_ARMED,
    FTS_STATE_TERMINATION_TRIGGERED,
    FTS_STATE_PARACHUTE_DEPLOYED,
    FTS_STATE_LINK_LOST
} fts_state_t;

typedef struct {
    platform_type_t platform;
    fts_state_t     state;
    uint32_t        last_heartbeat_ms;
    uint32_t        termination_timestamp_ms;
    bool            parachute_armed;
    bool            parachute_fired;
} fts_controller_t;

/* Низькорівневі апаратні виклики платформи */
extern uint32_t bsp_get_time_ms(void);
extern void     bsp_set_power_switch(bool enable);
extern void     bsp_set_parachute_pyro(bool fire);
extern void     bsp_emergency_disable_timer_pwm(void);
extern void     bsp_set_control_surfaces_spiral(void);

/* Розрахунок CRC16-CCITT (поліном 0x1021) */
static uint16_t fts_crc16(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFFU;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)((uint16_t)data[i] << 8);
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000U) {
                crc = (uint16_t)((crc << 1) ^ 0x1021U);
            } else {
                crc = (uint16_t)(crc << 1);
            }
        }
    }
    return crc;
}

void fts_init(fts_controller_t *ctrl, platform_type_t platform) {
    ctrl->platform = platform;
    ctrl->state = FTS_STATE_DISARMED;
    ctrl->last_heartbeat_ms = bsp_get_time_ms();
    ctrl->termination_timestamp_ms = 0;
    ctrl->parachute_armed = false;
    ctrl->parachute_fired = false;

    /* Початковий безпечний стан: силове живлення ESC вимкнено */
    bsp_set_power_switch(false);
    bsp_set_parachute_pyro(false);
    bsp_emergency_disable_timer_pwm();
}

void fts_trigger_termination(fts_controller_t *ctrl) {
    if (ctrl->state == FTS_STATE_TERMINATION_TRIGGERED || 
        ctrl->state == FTS_STATE_PARACHUTE_DEPLOYED) {
        return;
    }

    ctrl->state = FTS_STATE_TERMINATION_TRIGGERED;
    ctrl->termination_timestamp_ms = bsp_get_time_ms();

    /* 1. Миттєвий розрив силових ключів живлення ESC */
    bsp_set_power_switch(false);

    /* 2. Апаратне скидання біта MOE / вимкнення виходів ШІМ у таймері */
    bsp_emergency_disable_timer_pwm();

    /* 3. Специфічні дії для типу платформи */
    if (ctrl->platform == PLATFORM_FIXED_WING) {
        bsp_set_control_surfaces_spiral();
    }
}

void fts_process_incoming_packet(fts_controller_t *ctrl, const uint8_t *payload, size_t length) {
    if (length != 5 || payload[0] != FTS_MAGIC_BYTE) {
        return;
    }

    uint16_t received_crc = (uint16_t)((uint16_t)payload[3] << 8 | payload[4]);
    uint16_t calculated_crc = fts_crc16(payload, 3);

    if (received_crc != calculated_crc) {
        return; /* Пошкоджений пакет ігнорується */
    }

    ctrl->last_heartbeat_ms = bsp_get_time_ms();
    uint8_t cmd = payload[1];
    uint8_t aux = payload[2];

    if (cmd == FTS_CMD_KILL_POWER) {
        fts_trigger_termination(ctrl);
    } else if (cmd == FTS_CMD_ARM_SYSTEM && ctrl->state == FTS_STATE_DISARMED) {
        ctrl->state = FTS_STATE_ARMED;
        ctrl->parachute_armed = (aux != 0);
        bsp_set_power_switch(true);
    }
}

void fts_update_periodic(fts_controller_t *ctrl) {
    uint32_t now = bsp_get_time_ms();

    /* Контроль таймауту серцебиття FTS-радіолінка */
    if (ctrl->state == FTS_STATE_ARMED) {
        if ((now - ctrl->last_heartbeat_ms) > FTS_HEARTBEAT_TIMEOUT_MS) {
            ctrl->state = FTS_STATE_LINK_LOST;
            fts_trigger_termination(ctrl);
            return;
        }
    }

    /* Логіка послідовного відстрілу парашута */
    if (ctrl->state == FTS_STATE_TERMINATION_TRIGGERED && 
        ctrl->parachute_armed && 
        !ctrl->parachute_fired) {
        
        if ((now - ctrl->termination_timestamp_ms) >= PARACHUTE_DELAY_MS) {
            bsp_set_parachute_pyro(true);
            ctrl->parachute_fired = true;
            ctrl->state = FTS_STATE_PARACHUTE_DEPLOYED;
        }
    }
}
