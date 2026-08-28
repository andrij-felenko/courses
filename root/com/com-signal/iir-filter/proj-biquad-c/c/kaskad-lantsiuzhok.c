typedef struct {
    biquad_t *stage;      // масив ланок
    size_t    n;          // скільки їх
} biquad_chain_t;

float chain_step(biquad_chain_t *c, float x) {
    float v = x;
    for (size_t i = 0; i < c->n; ++i)
        v = biquad_step(&c->stage[i], v);   // вихід однієї → вхід наступної
    return v;
}
