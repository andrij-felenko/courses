#include <stdint.h>
#include <stdbool.h>

/* Константи та порогові значення силової шини */
#define VBUS_NOMINAL_MV      24000U
#define VBUS_CHOPPER_ON_MV   28000U
#define VBUS_CHOPPER_OFF_MV  26000U
#define VBUS_OVP_ALARM_MV    31000U
#define MAX_BRAKE_CURRENT_MA 15000U
#define ZERO_SPEED_RAD_S     2.0f

typedef enum {
    BRAKE_MODE_COAST = 0,
    BRAKE_MODE_DYNAMIC,
    BRAKE_MODE_REGEN,
    BRAKE_MODE_PLUG_EMERGENCY
} brake_mode_t;

typedef enum {
    DRIVE_STATE_IDLE = 0,
    DRIVE_STATE_RUNNING,
    DRIVE_STATE_BRAKING,
    DRIVE_STATE_HOLD_ZERO,
    DRIVE_STATE_FAULT_OVP
} drive_state_t;

typedef struct {
    drive_state_t state;
    brake_mode_t  mode;
    uint32_t      vbus_mv;
    int32_t       current_ma;
    float         speed_rad_s;
    uint16_t      pwm_duty_q12; /* 0..4095 */
    bool          chopper_active;
} motor_brake_controller_t;

/* Прототипи апаратного абстрактного рівня (HAL) */
void hal_set_hbridge_hiz(void);
void hal_set_hbridge_low_side_pwm(uint16_t duty_q12);
void hal_set_hbridge_reverse_plug(uint16_t duty_q12);
void hal_set_brake_chopper(bool enable);

void motor_brake_init(motor_brake_controller_t *ctrl) {
    ctrl->state = DRIVE_STATE_IDLE;
    ctrl->mode = BRAKE_MODE_COAST;
    ctrl->vbus_mv = VBUS_NOMINAL_MV;
    ctrl->current_ma = 0;
    ctrl->speed_rad_s = 0.0f;
    ctrl->pwm_duty_q12 = 0;
    ctrl->chopper_active = false;
    hal_set_hbridge_hiz();
    hal_set_brake_chopper(false);
}

void motor_brake_request(motor_brake_controller_t *ctrl, brake_mode_t mode) {
    if (ctrl->state == DRIVE_STATE_FAULT_OVP) {
        return; /* Заборона керування до скидання аварії */
    }
    ctrl->mode = mode;
    ctrl->state = DRIVE_STATE_BRAKING;
}

/* Викликається у високопріоритетному циклі керування (наприклад, 1 кГц / 1 мс) */
void motor_brake_process_1khz(motor_brake_controller_t *ctrl, 
                             uint32_t vbus_measured_mv, 
                             int32_t current_measured_ma, 
                             float current_speed_rad_s) {
    ctrl->vbus_mv = vbus_measured_mv;
    ctrl->current_ma = current_measured_ma;
    ctrl->speed_rad_s = current_speed_rad_s;

    /* 1. Апаратний захист від критичної перенапруги (OVP) */
    if (ctrl->vbus_mv >= VBUS_OVP_ALARM_MV) {
        ctrl->state = DRIVE_STATE_FAULT_OVP;
        hal_set_hbridge_hiz();
        hal_set_brake_chopper(true); /* Екстрене відкриття баласту */
        return;
    }

    /* 2. Гістерезисне керування гальмівним переривачем (Chopper) */
    if (ctrl->vbus_mv >= VBUS_CHOPPER_ON_MV) {
        ctrl->chopper_active = true;
        hal_set_brake_chopper(true);
    } else if (ctrl->vbus_mv <= VBUS_CHOPPER_OFF_MV) {
        ctrl->chopper_active = false;
        hal_set_brake_chopper(false);
    }

    /* 3. Кінцевий автомат стану гальмування */
    if (ctrl->state != DRIVE_STATE_BRAKING) {
        return;
    }

    /* Перевірка зупинки ротора */
    if (ctrl->speed_rad_s < ZERO_SPEED_RAD_S && ctrl->speed_rad_s > -ZERO_SPEED_RAD_S) {
        ctrl->state = DRIVE_STATE_HOLD_ZERO;
        ctrl->pwm_duty_q12 = 0;
        hal_set_hbridge_hiz();
        return;
    }

    switch (ctrl->mode) {
        case BRAKE_MODE_COAST:
            hal_set_hbridge_hiz();
            break;

        case BRAKE_MODE_DYNAMIC:
            /* Плавне наростання шпаруватості замикання нижніх ключів */
            if (ctrl->pwm_duty_q12 < 4095 - 64) {
                ctrl->pwm_duty_q12 += 64;
            } else {
                ctrl->pwm_duty_q12 = 4095;
            }
            /* Обмеження струму динамічного гальмування */
            if (ctrl->current_ma > (int32_t)MAX_BRAKE_CURRENT_MA && ctrl->pwm_duty_q12 > 128) {
                ctrl->pwm_duty_q12 -= 128;
            }
            hal_set_hbridge_low_side_pwm(ctrl->pwm_duty_q12);
            break;

        case BRAKE_MODE_REGEN:
            /* Спад робочого ШІМ для створення режиму генератора */
            if (ctrl->pwm_duty_q12 > 32) {
                ctrl->pwm_duty_q12 -= 32;
            } else {
                ctrl->pwm_duty_q12 = 0;
                /* Перехід на фінальне динамічне догальмовування */
                ctrl->mode = BRAKE_MODE_DYNAMIC;
            }
            break;

        case BRAKE_MODE_PLUG_EMERGENCY:
            /* Негайне увімкнення реверсу з жорстким контролем переходу через нуль */
            if (ctrl->speed_rad_s > 0.0f) {
                hal_set_hbridge_reverse_plug(2048); /* 50% зворотного ШІМ */
            } else {
                /* Миттєве вимкнення при зміні знака швидкості */
                ctrl->state = DRIVE_STATE_HOLD_ZERO;
                hal_set_hbridge_hiz();
            }
            break;
    }
}
