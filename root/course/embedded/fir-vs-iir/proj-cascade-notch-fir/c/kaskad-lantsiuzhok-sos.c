#include <stddef.h>

typedef struct {
    biquad_q31_t *stage;    // масив ланок (SOS)
    size_t        n;        // скільки їх
} sos_chain_t;

int32_t sos_step(sos_chain_t *c, int32_t x) {
    int32_t v = x;
    for (size_t i = 0; i < c->n; ++i)
        v = biquad_q31_step(&c->stage[i], v);   // вихід однієї → вхід наступної
    return v;
}

void sos_reset(sos_chain_t *c) {
    for (size_t i = 0; i < c->n; ++i)
        c->stage[i].x1 = c->stage[i].x2 = c->stage[i].y1 = c->stage[i].y2 = 0;
}
