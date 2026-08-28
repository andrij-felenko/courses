// Перетворення відліку звуку (−1..+1) на ширину імпульсу ШІМ.
// duty = 0.5 відповідає сигналу 0 (тиша = меандр 50%).
uint16_t sample_to_pwm(float sample, uint16_t period) {
    float duty = 0.5f + 0.5f * sample;   // −1→0.0, 0→0.5, +1→1.0
    if (duty < 0.0f) duty = 0.0f;        // захист від виходу за межі
    if (duty > 1.0f) duty = 1.0f;
    return (uint16_t)(duty * period + 0.5f);  // ширина в кроках таймера
}

// для sample = +0.5, period = 800:
// duty  = 0.5 + 0.5*0.5 = 0.75   →  75 %
// width = 0.75 * 800     = 600 кроків
