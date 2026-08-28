#include <complex.h>   // лише для офлайн-перевірки на ПК, не для прошивки
#include <stdio.h>

void comp_check_phase(comp_t *c, float w, float dt)
{
    float complex zinv = cexpf(-I * w * dt);                  // z⁻¹ = e^{−jωdt}
    float complex H = (c->b0 + c->b1 * zinv)
                    / (1.0f      + c->a1 * zinv);             // C(z) на частоті w
    float phase_deg = cargf(H) * 180.0f / 3.14159265f;       // фаза, градуси
    float mag       = cabsf(H);                               // підсилення, рази
    printf("на w=%.1f рад/с:  фаза=%.2f град,  |C|=%.3f\n", w, phase_deg, mag);
}
