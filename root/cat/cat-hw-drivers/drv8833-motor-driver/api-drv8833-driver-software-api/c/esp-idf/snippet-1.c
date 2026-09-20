#include <stdint.h>
#include <stdbool.h>

typedef enum {
    DRV8833_DECAY_SLOW = 0,
    DRV8833_DECAY_FAST = 1
} drv8833_decay_t;

typedef struct {
    uint8_t pin_in1;
    uint8_t pin_in2;
    uint8_t pin_nsleep;
    drv8833_decay_t decay_mode;
} drv8833_motor_t;

void drv8833_init(drv8833_motor_t *motor);
void drv8833_set_speed(drv8833_motor_t *motor, int16_t speed);
void drv8833_brake(drv8833_motor_t *motor);
void drv8833_stepper_step(drv8833_motor_t *motor_a, drv8833_motor_t *motor_b, uint8_t step_index);
