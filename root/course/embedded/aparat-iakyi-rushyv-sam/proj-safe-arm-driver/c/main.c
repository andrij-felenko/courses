#include <stdint.h>
#include <stdbool.h>

#define SAFETY_TOKEN_MAGIC  0x5A3C96E1U
#define PWM_MAX_DUTY        1000U
#define MIN_SAFE_VOLTAGE_MV 11000U
#define MAX_SAFE_VOLTAGE_MV 14500U

typedef enum {
    ACTUATOR_DISARMED = 0,
    ACTUATOR_ARM_REQUESTED,
    ACTUATOR_PRE_ARM_CHECK,
    ACTUATOR_ARMED,
    ACTUATOR_FAULT
} ActuatorState;

typedef struct {
    ActuatorState state;
    uint32_t last_heartbeat_ms;
    uint32_t arm_request_time_ms;
    uint16_t current_pwm;
    bool emergency_stop_active;
} SafeActuatorDriver;

// Платформні виклики керування регістрами GPIO та таймера
extern void hw_gpio_write_heartbeat(bool level);
extern void hw_timer_set_pwm_duty(uint16_t duty);
extern uint32_t hw_get_time_ms(void);
extern uint16_t hw_read_supply_voltage_mv(void);
extern bool hw_read_estop_pin(void);
extern void hw_watchdog_reset(void);

void safe_actuator_init(SafeActuatorDriver *drv) {
    // 1. Апаратні виходи встановлюємо в безпечний нуль ДО дозволу виходів
    hw_gpio_write_heartbeat(false);
    hw_timer_set_pwm_duty(0);

    drv->state = ACTUATOR_DISARMED;
    drv->last_heartbeat_ms = 0;
    drv->arm_request_time_ms = 0;
    drv->current_pwm = 0;
    drv->emergency_stop_active = false;
}

bool safe_actuator_request_arm(SafeActuatorDriver *drv, uint32_t token) {
    if (token != SAFETY_TOKEN_MAGIC) {
        drv->state = ACTUATOR_FAULT;
        return false;
    }
    if (drv->state != ACTUATOR_DISARMED) {
        return false;
    }
    drv->state = ACTUATOR_ARM_REQUESTED;
    drv->arm_request_time_ms = hw_get_time_ms();
    return true;
}

void safe_actuator_disarm(SafeActuatorDriver *drv) {
    // Миттєво зупиняємо генератор помпи та скидаємо ШІМ
    hw_gpio_write_heartbeat(false);
    hw_timer_set_pwm_duty(0);
    drv->current_pwm = 0;
    if (drv->state != ACTUATOR_FAULT) {
        drv->state = ACTUATOR_DISARMED;
    }
}

void safe_actuator_process_cycle(SafeActuatorDriver *drv, uint16_t target_pwm) {
    uint32_t now = hw_get_time_ms();
    drv->emergency_stop_active = hw_read_estop_pin();

    if (drv->emergency_stop_active) {
        safe_actuator_disarm(drv);
        drv->state = ACTUATOR_FAULT;
        return;
    }

    switch (drv->state) {
        case ACTUATOR_DISARMED:
            hw_gpio_write_heartbeat(false);
            hw_timer_set_pwm_duty(0);
            break;

        case ACTUATOR_ARM_REQUESTED:
            drv->state = ACTUATOR_PRE_ARM_CHECK;
            break;

        case ACTUATOR_PRE_ARM_CHECK: {
            uint16_t v_mv = hw_read_supply_voltage_mv();
            if (v_mv >= MIN_SAFE_VOLTAGE_MV && v_mv <= MAX_SAFE_VOLTAGE_MV) {
                drv->state = ACTUATOR_ARMED;
                drv->last_heartbeat_ms = now;
            } else {
                safe_actuator_disarm(drv);
                drv->state = ACTUATOR_FAULT;
            }
            break;
        }

        case ACTUATOR_ARMED: {
            // Генерація динамічного меандру серцебиття з періодом 1 мс (1 кГц)
            static bool hb_phase = false;
            hb_phase = !hb_phase;
            hw_gpio_write_heartbeat(hb_phase);
            drv->last_heartbeat_ms = now;

            if (target_pwm > PWM_MAX_DUTY) {
                target_pwm = PWM_MAX_DUTY;
            }
            drv->current_pwm = target_pwm;
            hw_timer_set_pwm_duty(drv->current_pwm);
            break;
        }

        case ACTUATOR_FAULT:
        default:
            safe_actuator_disarm(drv);
            break;
    }

    // Регулярне годування сторожового таймера
    hw_watchdog_reset();
}
