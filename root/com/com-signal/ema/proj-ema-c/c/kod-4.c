typedef struct {
    float level, trend;          /* оцінка рівня й оцінка тренду */
    float alpha, beta;           /* α — для рівня, β — для тренду */
    bool  primed;
} dema_t;

float dema_step(dema_t *f, float x) {
    if (!f->primed) {
        f->level = x; f->trend = 0.0f; f->primed = true;
        return f->level;
    }
    float prev = f->level;
    f->level += f->alpha * (x - f->level) + f->trend;       /* рівень + хід тренду */
    f->trend += f->beta  * ((f->level - prev) - f->trend);  /* оновлюємо сам тренд */
    return f->level;
}
