void biquad_reset_chain(biquad_chain_t *c) {
    for (size_t i = 0; i < c->n; ++i) {
        c->stage[i].x1 = c->stage[i].x2 = 0.0f;
        c->stage[i].y1 = c->stage[i].y2 = 0.0f;
    }
}

// Повертає 1, якщо хвіст згас (фільтр стабільний), інакше 0.
int biquad_is_stable(biquad_chain_t *c) {
    biquad_reset_chain(c);
    float out = chain_step(c, 1.0f);              // імпульс
    float peak = (out < 0 ? -out : out);
    for (int n = 1; n < 1000; ++n) {
        out = chain_step(c, 0.0f);               // далі — нулі
        float m = (out < 0 ? -out : out);
        if (m > peak) peak = m;
        if (m > 1e6f) { biquad_reset_chain(c); return 0; }  // вибухає
    }
    biquad_reset_chain(c);
    return (out < 1e-3f && out > -1e-3f);         // хвіст справді згас
}
