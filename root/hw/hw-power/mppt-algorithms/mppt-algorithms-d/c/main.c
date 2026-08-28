// Один крок Perturb & Observe. Викликати періодично — але тільки
// ПІСЛЯ того, як напруга й струм устигли влягтися від минулого кроку.
static uint16_t duty;            // поточна шпаруватість (одиниці таймера ШІМ)
static float    p_prev;          // потужність на минулому кроці
static int8_t   dir = +1;        // напрям останнього кроку: +1 або −1
static const uint16_t STEP = 4;  // розмір кроку шпаруватості

void mppt_po_step(void) {
    float v = adc_panel_voltage();   // усереднене значення з АЦП
    float i = adc_panel_current();
    float p = v * i;

    if (p < p_prev)                  // потужність упала —
        dir = -dir;                  //   розвернути напрям

    duty += dir * STEP;              // крок у (можливо новому) напрямі
    duty  = clamp_u16(duty, DUTY_MIN, DUTY_MAX);   // не вилізти за межі
    pwm_set_duty(duty);

    p_prev = p;                      // запам'ятати для наступного порівняння
}
