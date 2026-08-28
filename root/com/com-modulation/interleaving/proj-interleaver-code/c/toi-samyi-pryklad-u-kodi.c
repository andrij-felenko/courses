#include <stdint.h>
#include <string.h>

#define N 6                        /* число гілок (позицій комутатора)  */
#define M 2                        /* приріст затримки на гілку          */
#define MEM (M * N * (N - 1) / 2)  /* сумарна пам'ять = рівно 30 комірок */

typedef struct {
    uint8_t  buf[MEM];             /* плаский буфер під усі гілки        */
    uint16_t base[N], curs[N], len[N];
    uint8_t  br;                   /* поточна гілка (комутатор)          */
} interleaver_t;

/* delays[i] — довжина лінії затримки гілки i у комірках */
static void il_init(interleaver_t *it, const uint16_t delays[N]) {
    uint16_t off = 0;
    for (int i = 0; i < N; i++) {
        it->len[i]  = delays[i];
        it->base[i] = off;         /* де в буфері починається кільце гілки i */
        it->curs[i] = 0;
        off += delays[i];
    }
    it->br = 0;
    memset(it->buf, 0, sizeof it->buf);     /* прайм: перші символи — фіктивні */
}

static uint8_t il_step(interleaver_t *it, uint8_t s) {
    uint8_t i = it->br;
    it->br = (uint8_t)((it->br + 1) % N);    /* комутатор крутиться по колу */
    if (it->len[i] == 0) return s;           /* гілка 0 — наскрізь          */
    uint16_t k = (uint16_t)(it->base[i] + it->curs[i]);
    uint8_t out = it->buf[k];                /* найстаріший символ гілки виходить */
    it->buf[k] = s;                          /* новий стає на його місце          */
    it->curs[i] = (uint16_t)((it->curs[i] + 1) % it->len[i]);
    return out;
}

/* Заведення пари: перемішувач і дзеркальний зворотний.
   interleaver_t tx, rx;
   uint16_t fwd[N], rev[N];
   for (int i = 0; i < N; i++) { fwd[i] = i * M; rev[i] = (N - 1 - i) * M; }
   il_init(&tx, fwd);                        // затримки 0, M, 2M, … (N−1)M
   il_init(&rx, rev);                        // затримки (N−1)M, … M, 0
   uint8_t chan = il_step(&tx, symbol);      // у канал
   uint8_t back = il_step(&rx, chan);        // з каналу, зсув M·N·(N−1) символів */
