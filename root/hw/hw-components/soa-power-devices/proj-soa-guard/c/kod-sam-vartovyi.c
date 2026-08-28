#include <math.h>
#include <stdbool.h>

#define SOA_STAGES 5

typedef struct {
    float a[SOA_STAGES];   /* e^(-dt/tau_i) — скільки лишилося від старого */
    float g[SOA_STAGES];   /* R_i*(1 - a_i) — скільки долилося від нового  */
    float t[SOA_STAGES];   /* стан: внесок ланки в перегрів, К            */
} soa_model;

/* r[], tau[] — мережа Фостера приладу; dt — крок семплювання, с */
void soa_init(soa_model *m, const float *r, const float *tau, float dt)
{
    for (int i = 0; i < SOA_STAGES; i++) {
        m->a[i] = expf(-dt / tau[i]);
        m->g[i] = r[i] * (1.0f - m->a[i]);
        m->t[i] = 0.0f;
    }
}

/* Один крок. p — миттєва потужність на ключі, Вт.
   Повертає перегрів переходу над корпусом, К. */
float soa_step(soa_model *m, float p)
{
    float rise = 0.0f;
    for (int i = 0; i < SOA_STAGES; i++) {
        m->t[i] = m->t[i] * m->a[i] + p * m->g[i];
        rise += m->t[i];
    }
    return rise;
}
