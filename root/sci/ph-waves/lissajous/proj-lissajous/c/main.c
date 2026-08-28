#include <math.h>
#include <stdint.h>

/* Потоковий вимір зсуву фаз між двома каналами однакової частоти.
   Стан — дев'ять float і лічильник, сорок байтів; на відлік O(1). */
typedef struct {
    float a_dc;                  /* полюс фільтра сталої складової */
    float dc_x, dc_y;            /* повільні середні каналів */
    float prev_x, prev_y;        /* попередні центровані відліки */
    float sxx, syy, sxy;         /* суми квадратів і добутку */
    float area2;                 /* подвоєна орієнтована площа */
    uint32_t n;
} xyphase_t;

void xyphase_restart(xyphase_t *s) {          /* нове вікно; середні лишаємо */
    s->sxx = s->syy = s->sxy = s->area2 = 0.0f;
    s->prev_x = s->prev_y = 0.0f;
    s->n = 0;
}

void xyphase_init(xyphase_t *s, float fs, float dc_hz) {
    s->a_dc = expf(-6.2831853f * dc_hz / fs);  /* зріз dc_hz далеко нижче сигналу */
    s->dc_x = s->dc_y = 0.0f;
    xyphase_restart(s);
}

void xyphase_push(xyphase_t *s, float x, float y) {
    s->dc_x += (1.0f - s->a_dc) * (x - s->dc_x);   /* однополюсне середнє */
    s->dc_y += (1.0f - s->a_dc) * (y - s->dc_y);
    const float cx = x - s->dc_x;                  /* центровані відліки */
    const float cy = y - s->dc_y;

    s->sxx += cx * cx;
    s->syy += cy * cy;
    s->sxy += cx * cy;
    if (s->n)                                      /* косий добуток пари сусідів */
        s->area2 += s->prev_x * cy - cx * s->prev_y;

    s->prev_x = cx;
    s->prev_y = cy;
    s->n++;
}

float xyphase_read(const xyphase_t *s) {           /* зсув фаз у радіанах */
    const float den = sqrtf(s->sxx * s->syy);
    if (den < 1e-12f) return 0.0f;
    float c = s->sxy / den;
    if (c >  1.0f) c =  1.0f;
    if (c < -1.0f) c = -1.0f;
    const float phi = acosf(c);
    return (s->area2 < 0.0f) ? -phi : phi;         /* обхід задає знак */
}
