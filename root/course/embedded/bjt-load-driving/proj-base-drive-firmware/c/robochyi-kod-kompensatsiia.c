// ── ШІМ-таймер керує базою; компенсуємо сховок, вкорочуючи час ON. ──
#define PWM_TIMER_HZ    84000000u    // частота ШІМ-таймера (може відрізнятись!)
#define PWM_PERIOD      4200u        // ARR+1: 84e6 / 4200 = 20 кГц

static uint32_t g_dead_ticks = 0;    // мертвий час, переведений у тики ШІМ

// Викликати раз після вимірювання: закешувати t_dead у тиках ШІМ-таймера.
void pwm_set_dead_time_ns(uint32_t t_dead_ns)
{
    // ticks = t_dead_ns * f_pwm / 1e9   (у 64-біт проти переповнення)
    g_dead_ticks = (uint32_t)(((uint64_t)t_dead_ns * PWM_TIMER_HZ) / 1000000000ull);
}

// Виставити БАЖАНУ шпаруватість 0..PWM_PERIOD; всередині вкорочуємо на сховок.
void pwm_set_duty_compensated(uint32_t desired_on_ticks)
{
    uint32_t on = desired_on_ticks;

    // Компенсація: реальний струм тече на g_dead_ticks довше → команду вкоротити.
    if (on > g_dead_ticks) {
        on -= g_dead_ticks;
    } else {
        on = 0;              // бажаний ON коротший за сам сховок — чесний нуль
    }
    // Насичення в межах періоду.
    if (on > PWM_PERIOD) on = PWM_PERIOD;

    PWM_TIM->CCR1 = on;      // апаратно застосується з наступного циклу
}
