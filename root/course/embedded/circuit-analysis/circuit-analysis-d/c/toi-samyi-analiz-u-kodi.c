#include <stdio.h>

/* Напруга одного вузла, до якого приходять джерела Vk через Rk
   і висять резистори на землю Rg[]. Це прямий запис вузлового рівняння:
   V_вузла = (Σ Vk·Gk) / (Σ Gk усіх приєднаних провідностей).           */
static float node_voltage(const float *v_src, const float *r_src, int ns,
                          const float *r_gnd, int ng) {
    float sum_g = 0.0f;   /* знаменник: сума ВСІХ провідностей вузла */
    float sum_ig = 0.0f;  /* чисельник: сума струмів, вкинутих джерелами */
    for (int k = 0; k < ns; k++) {      /* джерела напруги через резистор */
        float g = 1.0f / r_src[k];
        sum_g  += g;
        sum_ig += v_src[k] * g;         /* внесок джерела = Vk·Gk (струм) */
    }
    for (int k = 0; k < ng; k++)        /* пасивні резистори на землю */
        sum_g += 1.0f / r_gnd[k];
    return sum_ig / sum_g;
}

int main(void) {
    /* Приклад 2: V1=10В через 10Ω, V2=6В через 10Ω; R3=20Ω на землю */
    float vs[] = {10.0f, 6.0f};
    float rs[] = {10.0f, 10.0f};
    float rg[] = {20.0f};
    float va = node_voltage(vs, rs, 2, rg, 1);
    printf("V(A) = %.2f В\n", va);       /* 6.40 В — як руками й вузловим методом */
    return 0;
}
