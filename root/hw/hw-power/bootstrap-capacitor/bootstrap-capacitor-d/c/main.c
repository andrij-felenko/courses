// ШІМ верхнього ключа півмоста через таймер MCU.
// Cbs заряджається лише коли верхній ВИМКНЕНО (SW падає до землі).
// Тому НІКОЛИ не даємо повні 100% — лишаємо «вікно» на перезаряд.
#define PWM_TOP          1000u   // період таймера (0..TOP)
#define DUTY_CEILING_PCT 95u     // стеля шпаруватості заради бутстрепа

uint16_t clamp_duty(uint16_t duty) {
    uint16_t ceil = (uint32_t)PWM_TOP * DUTY_CEILING_PCT / 100u;  // = 950
    if (duty > ceil)
        duty = ceil;             // лишаємо ≥5% часу на заряд Cbs
    return duty;
}
