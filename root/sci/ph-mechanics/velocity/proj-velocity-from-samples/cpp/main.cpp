#include <stdint.h>

#define NW 7                  /* довжина вікна (непарна)        */
#define MW ((NW - 1) / 2)     /* напівширина = 3                */

typedef struct {
    int32_t buf[NW];   /* кільце сирих відліків (напр. лічильник енкодера) */
    int     head;      /* куди ляже наступний відлік                       */
    int     filled;    /* скільки вже покладено (до NW)                    */
    float   inv_dt;    /* 1/Δt, Гц                                         */
} Slope;

void slope_init(Slope *s, float dt)
{
    s->head = 0;  s->filled = 0;  s->inv_dt = 1.0f / dt;
}

/* Покласти новий відлік x; повернути оцінку швидкості (одиниць/с).
   Оцінка стосується ЦЕНТРУ вікна — тобто відстає на MW·Δt. */
float slope_push(Slope *s, int32_t x)
{
    s->buf[s->head] = x;
    s->head = (s->head + 1) % NW;
    if (s->filled < NW) {            /* вікно ще не повне */
        s->filled++;
        return 0.0f;
    }
    /* найстаріший відлік — саме там, куди тепер вказує head */
    int64_t num = 0;                 /* int64: k·counts не перекине розрядність */
    int idx = s->head;
    for (int k = -MW; k <= MW; k++) {
        num += (int64_t)k * s->buf[idx];
        idx = (idx + 1) % NW;
    }
    const int32_t SUMK2 = MW * (MW + 1) * (2 * MW + 1) / 3;   /* =28 при NW=7 */
    return (float)num / (float)SUMK2 * s->inv_dt;
}
