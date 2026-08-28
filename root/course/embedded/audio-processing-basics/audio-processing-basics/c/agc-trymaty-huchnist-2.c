float gain = 1.0f;
const float target = 3000.0f;
const float atk = 0.25f;    // частка кроку вниз за буфер — швидко (атака)
const float rel = 0.02f;    // частка кроку вгору за буфер — повільно (відпускання)
const float max_gain = 32.0f;

void agc_process(int16_t *buf, int n) {
    float level = rms_level(buf, n) * gain;
    if (level > 1.0f) {
        float want = gain * (target / level);   // куди хотіли б прийти
        if (want > max_gain) want = max_gain;    // стеля: не роздувати шум у паузі
        float step = (want < gain) ? atk : rel;  // вниз швидко, вгору повільно
        gain += step * (want - gain);            // повземо до цілі, не стрибаємо
    }
    for (int i = 0; i < n; i++) {
        int32_t y = (int32_t)(buf[i] * gain);
        if (y >  32767) y =  32767;
        if (y < -32768) y = -32768;
        buf[i] = (int16_t)y;
    }
}
