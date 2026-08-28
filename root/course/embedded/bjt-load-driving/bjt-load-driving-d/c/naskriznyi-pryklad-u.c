// М'який старт моторчика на нижньому NPN-ключі через апаратний ШІМ.
// Нарощуємо шпаруватість поступово — щоб пусковий струм не викинув
// робочу точку транзистора за межу другого пробою (SOA).

#define PWM_MAX      1000u      // повна шпаруватість (100%)
#define RAMP_STEP    10u        // приріст за один тік
#define RAMP_TICK_MS 5u         // період нарощування

static uint16_t duty = 0;       // поточна шпаруватість

void motor_soft_start_tick(void) {
    if (duty < PWM_MAX) {
        duty += RAMP_STEP;              // +1% кожні 5 мс → повний хід за ~0.5 с
        if (duty > PWM_MAX) duty = PWM_MAX;
        pwm_set_duty(PWM_CH_MOTOR, duty);
    }
}

void motor_stop(void) {
    duty = 0;
    pwm_set_duty(PWM_CH_MOTOR, 0);      // знімаємо ШІМ — ключ закритий
}
