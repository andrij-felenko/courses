#include <stdint.h>

#define NTAPS 31                 /* непарне: є центральний відвід */

typedef struct {
    float  b[NTAPS];             /* коефіцієнти (імпульсна характеристика) */
    float  buf[NTAPS];           /* кільцевий буфер відліків */
    int    head;                 /* індекс найновішого відліку */
} FirF;

void firf_init(FirF *f, const float *taps)
{
    for (int i = 0; i < NTAPS; i++) { f->b[i] = taps[i]; f->buf[i] = 0.0f; }
    f->head = 0;
}

float firf_step(FirF *f, float x)
{
    f->buf[f->head] = x;                 /* новий відлік у голову */

    float acc = 0.0f;
    int idx = f->head;
    for (int k = 0; k < NTAPS; k++) {
        acc += f->b[k] * f->buf[idx];    /* згортка b[k]·x[n−k] */
        idx = (idx == 0) ? NTAPS - 1 : idx - 1;   /* назад по колу */
    }

    f->head = (f->head + 1) % NTAPS;     /* голова — вперед по колу */
    return acc;
}
