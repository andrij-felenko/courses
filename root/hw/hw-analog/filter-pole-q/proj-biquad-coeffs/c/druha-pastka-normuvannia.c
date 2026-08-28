// Прикласти загальний множник підсилення до ланки (масштабує лише чисельник —
// полюси не чіпаємо, форма АЧХ та сама, змінюється тільки рівень).
static void biquad_scale_gain(biquad *bq, float g)
{
    bq->b0 *= g;
    bq->b1 *= g;
    bq->b2 *= g;
}

// Підсилення каскаду на ПОСТІЙНОМУ струмі (нульовій частоті): добуток
// підсилень ланок, кожне = (b0+b1+b2)/(1+a1+a2). Має бути ≈ 1 для ФНЧ.
static float cascade_dc_gain(const biquad_cascade *c)
{
    float g = 1.0f;
    for (uint8_t i = 0; i < c->n; i++) {
        const biquad *b = &c->stage[i];
        g *= (b->b0 + b->b1 + b->b2) / (1.0f + b->a1 + b->a2);
    }
    return g;
}
