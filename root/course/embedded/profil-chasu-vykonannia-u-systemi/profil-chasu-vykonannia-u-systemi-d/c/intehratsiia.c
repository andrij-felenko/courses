/* Приклад використання профілювальника у коді на C */
#include "task_profiler.h"
#include "gpio_profiling.h"

#define TASK_MOTOR_ID 0

void Motor_Control_Loop(void) {
    /* 1. Фіксація моменту початку виконання задачі */
    task_profiler_enter(TASK_MOTOR_ID);
    prof_pin_high(PROF_PIN_TASK1);
    
    /* 2. Корисна робота алгоритму */
    Read_ADC_Currents();
    Clarke_Park_Transform();
    Run_PI_Regulators();
    Update_PWM_Duty();
    
    /* 3. Фіксація завершення */
    prof_pin_low(PROF_PIN_TASK1);
    task_profiler_exit(TASK_MOTOR_ID);
}
