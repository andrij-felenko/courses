// Керування H-мостом на мікроконтролері STM32: таймер ШІМ на 16 кГц та плавний пуск
#include "main.h"

extern TIM_HandleTypeDef htim1; // Таймер налаштовано на частоту 16 кГц (ARR = 1000)

#define MOTOR_IN1_PIN       GPIO_PIN_8
#define MOTOR_IN1_PORT      GPIOB
#define MOTOR_IN2_PIN       GPIO_PIN_9
#define MOTOR_IN2_PORT      GPIOB
#define MOTOR_PWM_CHANNEL   TIM_CHANNEL_1

typedef enum {
    MOTOR_STOP,
    MOTOR_FORWARD,
    MOTOR_REVERSE,
    MOTOR_BRAKE
} MotorState_t;

typedef struct {
    MotorState_t state;
    uint16_t current_ccr; // Поточне значення регістру порівняння (0..1000)
    uint16_t target_ccr;  // Цільове значення шпаруватості (0..1000)
    uint32_t last_update; // Таймстемп останнього кроку наростання
} MotorController_t;

static MotorController_t motor = {
    .state = MOTOR_STOP,
    .current_ccr = 0,
    .target_ccr = 0,
    .last_update = 0
};

void motor_set_direction(MotorState_t new_state) {
    motor.state = new_state;
    switch (new_state) {
        case MOTOR_FORWARD:
            HAL_GPIO_WritePin(MOTOR_IN1_PORT, MOTOR_IN1_PIN, GPIO_PIN_SET);
            HAL_GPIO_WritePin(MOTOR_IN2_PORT, MOTOR_IN2_PIN, GPIO_PIN_RESET);
            break;
        case MOTOR_REVERSE:
            HAL_GPIO_WritePin(MOTOR_IN1_PORT, MOTOR_IN1_PIN, GPIO_PIN_RESET);
            HAL_GPIO_WritePin(MOTOR_IN2_PORT, MOTOR_IN2_PIN, GPIO_PIN_SET);
            break;
        case MOTOR_BRAKE:
            // Активне гальмування: замикання обмотки через обидва нижні ключі
            HAL_GPIO_WritePin(MOTOR_IN1_PORT, MOTOR_IN1_PIN, GPIO_PIN_SET);
            HAL_GPIO_WritePin(MOTOR_IN2_PORT, MOTOR_IN2_PIN, GPIO_PIN_SET);
            motor.current_ccr = 1000;
            motor.target_ccr = 1000;
            __HAL_TIM_SET_COMPARE(&htim1, MOTOR_PWM_CHANNEL, 1000);
            return;
        case MOTOR_STOP:
        default:
            // Вільний вибіг: ключі закриті
            HAL_GPIO_WritePin(MOTOR_IN1_PORT, MOTOR_IN1_PIN, GPIO_PIN_RESET);
            HAL_GPIO_WritePin(MOTOR_IN2_PORT, MOTOR_IN2_PIN, GPIO_PIN_RESET);
            motor.current_ccr = 0;
            motor.target_ccr = 0;
            __HAL_TIM_SET_COMPARE(&htim1, MOTOR_PWM_CHANNEL, 0);
            return;
    }
}

void motor_process_ramp(void) {
    uint32_t now = HAL_GetTick();
    if (now - motor.last_update >= 5) { // Крок кожні 5 мс
        motor.last_update = now;

        if (motor.current_ccr < motor.target_ccr) {
            motor.current_ccr += 20; // Приріст 2% за крок (розгін за 250 мс)
            if (motor.current_ccr > motor.target_ccr) {
                motor.current_ccr = motor.target_ccr;
            }
            __HAL_TIM_SET_COMPARE(&htim1, MOTOR_PWM_CHANNEL, motor.current_ccr);
        } else if (motor.current_ccr > motor.target_ccr) {
            if (motor.current_ccr > 40) {
                motor.current_ccr -= 40;
            } else {
                motor.current_ccr = 0;
            }
            if (motor.current_ccr < motor.target_ccr) {
                motor.current_ccr = motor.target_ccr;
            }
            __HAL_TIM_SET_COMPARE(&htim1, MOTOR_PWM_CHANNEL, motor.current_ccr);
        }
    }
}

void motor_init(void) {
    HAL_TIM_PWM_Start(&htim1, MOTOR_PWM_CHANNEL);
    motor_set_direction(MOTOR_STOP);
}
