// Каскад біквадів: фільтр довільного (парного) порядку.
typedef struct {
    biquad *stage;     // масив ланок
    uint8_t n;         // кількість ланок (порядок = 2·n)
} biquad_cascade;

// Прогнати один семпл крізь увесь каскад (ланка за ланкою).
static float cascade_process(biquad_cascade *c, float x)
{
    for (uint8_t i = 0; i < c->n; i++)
        x = biquad_process(&c->stage[i], x);   // вихід → вхід наступної
    return x;
}

// Скинути пам'ять усіх ланок каскаду.
static void cascade_reset(biquad_cascade *c)
{
    for (uint8_t i = 0; i < c->n; i++)
        biquad_reset(&c->stage[i]);
}
