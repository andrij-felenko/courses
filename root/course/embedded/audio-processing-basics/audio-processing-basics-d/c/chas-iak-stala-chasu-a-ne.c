#include <math.h>

typedef struct {
    float gain;          // поточне підсилення (лінійне)
    float target;        // цільовий RMS
    float a_atk, a_rel;  // коефіцієнти EMA, пораховані з часів
    float max_gain;      // стеля проти витягування шуму
} agc_state;

// Виклик раз при налаштуванні: перевести часи в коефіцієнти.
void agc_init(agc_state *s, float target, float atk_s, float rel_s,
              float buf_s, float max_gain) {
    s->gain     = 1.0f;
    s->target   = target;
    s->max_gain = max_gain;
    s->a_atk = 1.0f - expf(-buf_s / atk_s);   // швидкий (малий τ → α ближче до 1)
    s->a_rel = 1.0f - expf(-buf_s / rel_s);   // повільний (великий τ → α мале)
}

void agc_process(agc_state *s, int16_t *buf, int n) {
    float level = level_rms() * s->gain;      // рівень ПІСЛЯ поточного підсилення
    if (level > 1.0f) {
        float want = s->gain * (s->target / level);   // куди хотіли б прийти
        if (want > s->max_gain) want = s->max_gain;    // стеля
        float a = (want < s->gain) ? s->a_atk : s->a_rel;  // вниз швидко, вгору повільно
        s->gain += a * (want - s->gain);      // повземо до цілі
    }
    for (int i = 0; i < n; i++) {
        int32_t y = (int32_t)(buf[i] * s->gain);
        if (y >  32767) y =  32767;
        if (y < -32768) y = -32768;
        buf[i] = (int16_t)y;
    }
}
