#include <math.h>
#include <stdint.h>

/* Онлайн-оцінка частоти биття на МК: |x| -> каскад ФНЧ = обвідна;
   рахуємо перетини обвідної через повільне середнє знизу вгору.   */
typedef struct {
    float a_env;                 /* полюс кожного ступеня ФНЧ обвідної */
    float a_mean;                /* полюс повільного порога-середнього */
    float lp[3];                 /* стан 3-ступеневого каскаду         */
    float mean, prev;
    uint32_t crossings;
} beat_t;

void beat_init(beat_t *b, float fs, float env_hz, float mean_hz) {
    b->a_env  = expf(-2.0f * (float)M_PI * env_hz  / fs);
    b->a_mean = expf(-2.0f * (float)M_PI * mean_hz / fs);
    b->lp[0] = b->lp[1] = b->lp[2] = 0.0f;
    b->mean  = b->prev = 0.0f;
    b->crossings = 0;
}

void beat_push(beat_t *b, float x) {
    float v = fabsf(x);                       /* випрямлення */
    for (int i = 0; i < 3; i++)               /* каскад -> крутіший спад */
        v = b->lp[i] = b->a_env * b->lp[i] + (1.0f - b->a_env) * v;
    b->mean = b->a_mean * b->mean + (1.0f - b->a_mean) * v;
    if (b->prev <= b->mean && v > b->mean)    /* перетин порога вгору */
        b->crossings++;
    b->prev = v;
}

/* після вікна тривалістю window_s: оцінка й скидання */
float beat_read(beat_t *b, float window_s) {
    float f = (float)b->crossings / window_s;
    b->crossings = 0;
    return f;
}
