/* rc_safety_module.c - Модуль декодування та захисту каналів керування */
#include <stdint.h>
#include <stdbool.h>

#define RC_DEADBAND_US          25U
#define RC_THROTTLE_ARM_MAX_US  1050U
#define RC_SWITCH_LOW_US        1300U
#define RC_SWITCH_HIGH_US       1700U

/* Бітові прапорці блокування запуску двигунів */
typedef enum {
    ARM_OK                       = 0x0000,
    ARM_BLOCK_THROTTLE_NOT_ZERO  = 0x0001,
    ARM_BLOCK_PREARM_MISSING     = 0x0002,
    ARM_BLOCK_FAILSAFE_ENGAGED   = 0x0004,
    ARM_BLOCK_SWITCH_NOT_RESET   = 0x0008,
    ARM_BLOCK_SENSOR_NOT_READY   = 0x0010
} arming_error_mask_t;

/* Дискретні позиції перемикачів */
typedef enum {
    SW_POS_LOW    = 0,
    SW_POS_MID    = 1,
    SW_POS_HIGH   = 2,
    SW_POS_INVALID = 3
} switch_pos_t;

/* Структура вхідних радіоканалів */
typedef struct {
    uint16_t throttle_us;
    uint16_t arm_switch_us;
    uint16_t prearm_btn_us;
    uint16_t mode_switch_us;
    bool     failsafe_active;
    bool     sensors_healthy;
} rc_input_frame_t;

/* Внутрішній стан системи безпеки */
typedef struct {
    bool                is_armed;
    bool                arm_switch_was_high_on_boot;
    arming_error_mask_t last_error_flags;
} safety_state_t;

static safety_state_t g_safety_state = {
    .is_armed = false,
    .arm_switch_was_high_on_boot = true,
    .last_error_flags = ARM_OK
};

/* Декодування 3-позиційного каналу з гістерезисним захистом */
switch_pos_t rc_decode_3pos(uint16_t pulse_us) {
    if (pulse_us < 800U || pulse_us > 2200U) {
        return SW_POS_INVALID;
    }
    if (pulse_us < (RC_SWITCH_LOW_US - RC_DEADBAND_US)) {
        return SW_POS_LOW;
    }
    if (pulse_us > (RC_SWITCH_HIGH_US + RC_DEADBAND_US)) {
        return SW_POS_HIGH;
    }
    if (pulse_us >= (RC_SWITCH_LOW_US + RC_DEADBAND_US) &&
        pulse_us <= (RC_SWITCH_HIGH_US - RC_DEADBAND_US)) {
        return SW_POS_MID;
    }
    return SW_POS_MID; /* Збереження попереднього стану в зоні гістерезису */
}

/* Перевірка умов активації та оновлення стану моторів */
bool rc_process_arming_logic(const rc_input_frame_t *frame) {
    if (frame == NULL) {
        return false;
    }

    bool arm_requested = (frame->arm_switch_us > RC_SWITCH_HIGH_US);
    bool prearm_active = (frame->prearm_btn_us > RC_SWITCH_HIGH_US);

    /* Захист від старту з увімкненим тумблером під час подачі живлення */
    if (g_safety_state.arm_switch_was_high_on_boot) {
        if (!arm_requested) {
            g_safety_state.arm_switch_was_high_on_boot = false;
        } else {
            g_safety_state.is_armed = false;
            g_safety_state.last_error_flags = ARM_BLOCK_SWITCH_NOT_RESET;
            return false;
        }
    }

    /* Якщо надійшла команда вимкнення - негайне роззброєння */
    if (!arm_requested) {
        g_safety_state.is_armed = false;
        g_safety_state.last_error_flags = ARM_OK;
        return false;
    }

    /* Якщо вже зведено - підтримуємо стан до зняття тумблера */
    if (g_safety_state.is_armed) {
        return true;
    }

    /* Перевірка інтерлоків перед переходом у стан ARMED */
    arming_error_mask_t errors = ARM_OK;

    if (frame->throttle_us > RC_THROTTLE_ARM_MAX_US) {
        errors |= ARM_BLOCK_THROTTLE_NOT_ZERO;
    }
    if (!prearm_active) {
        errors |= ARM_BLOCK_PREARM_MISSING;
    }
    if (frame->failsafe_active) {
        errors |= ARM_BLOCK_FAILSAFE_ENGAGED;
    }
    if (!frame->sensors_healthy) {
        errors |= ARM_BLOCK_SENSOR_NOT_READY;
    }

    g_safety_state.last_error_flags = errors;

    if (errors == ARM_OK) {
        g_safety_state.is_armed = true;
        return true;
    }

    g_safety_state.is_armed = false;
    return false;
}
