#include <stdint.h>
#include <stdbool.h>

#define ARM_MAGIC_TOKEN     0x5A3C96E1U
#define PWM_MAX_LIMIT       1000U
#define SAFE_VOLTAGE_MIN_MV 11000U

typedef enum {
    SAFE_STATE_DISARMED = 0,
    SAFE_STATE_PRE_ARM_TEST,
    SAFE_STATE_ARMED,
    SAFE_STATE_FAULT
} SafeState;

typedef struct {
    SafeState state;
    uint16_t current_pwm;
    bool estop_pressed;
} MotorSafetyController;

// Апаратні абстракції периферії
extern void hw_set_heartbeat_pin(bool level);
extern void hw_set_pwm_duty(uint16_t duty);
extern uint16_t hw_get_battery_voltage_mv(void);
extern bool hw_read_estop_active(void);

void motor_safety_init(MotorSafetyController *ctrl) {
    // 1. Примусове знеструмлення виходів ДО налаштування
    hw_set_heartbeat_pin(false);
    hw_set_pwm_duty(0);

    ctrl->state = SAFE_STATE_DISARMED;
    ctrl->current_pwm = 0;
    ctrl->estop_pressed = false;
}

bool motor_safety_arm(MotorSafetyController *ctrl, uint32_t token) {
    if (token != ARM_MAGIC_TOKEN || ctrl->state != SAFE_STATE_DISARMED) {
        ctrl->state = SAFE_STATE_FAULT;
        return false;
    }
    
    // Перевірка умов безпеки перед подачею сили
    if (hw_read_estop_active() || hw_get_battery_voltage_mv() < SAFE_VOLTAGE_MIN_MV) {
        ctrl->state = SAFE_STATE_FAULT;
        return false;
    }

    ctrl->state = SAFE_STATE_ARMED;
    return true;
}

void motor_safety_update(MotorSafetyController *ctrl, uint16_t target_pwm) {
    if (hw_read_estop_active()) {
        // Миттєве апаратне знеструмлення
        hw_set_heartbeat_pin(false);
        hw_set_pwm_duty(0);
        ctrl->state = SAFE_STATE_FAULT;
        return;
    }

    if (ctrl->state == SAFE_STATE_ARMED) {
        // Генерація меандру серцебиття для помпи заряду
        static bool hb_toggle = false;
        hb_toggle = !hb_toggle;
        hw_set_heartbeat_pin(hb_toggle);

        ctrl->current_pwm = (target_pwm > PWM_MAX_LIMIT) ? PWM_MAX_LIMIT : target_pwm;
        hw_set_pwm_duty(ctrl->current_pwm);
    } else {
        hw_set_heartbeat_pin(false);
        hw_set_pwm_duty(0);
    }
}
