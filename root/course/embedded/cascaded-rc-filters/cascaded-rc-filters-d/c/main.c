// Одна цифрова RC-ланка нижніх частот (експоненційний згладжувач).
// alpha = dt / (RC + dt), 0 < alpha < 1; менше alpha — повільніше, сильніше згладжує.
typedef struct {
    float y;       // попередній вихід (стан ланки)
    float alpha;   // коефіцієнт згладжування
} RcStage;

static inline float rc_step(RcStage *s, float x) {
    s->y += s->alpha * (x - s->y);   // y += α·(вхід − y)
    return s->y;
}
