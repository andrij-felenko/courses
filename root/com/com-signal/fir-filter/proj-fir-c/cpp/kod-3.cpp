#include <stdint.h>

#define QSHIFT 15                /* формат Q15: 1.0 == 32768 */

typedef struct {
    int16_t b[NTAPS];            /* коефіцієнти у Q15 */
    int16_t buf[NTAPS];
    int     head;
} FirQ;

int16_t firq_step(FirQ *f, int16_t x)
{
    f->buf[f->head] = x;

    int64_t acc = 0;             /* ширший за відліки — проти переповнення */
    int idx = f->head;
    for (int k = 0; k < NTAPS; k++) {
        acc += (int32_t)f->b[k] * (int32_t)f->buf[idx];   /* int16·int16 → int32 */
        idx = (idx == 0) ? NTAPS - 1 : idx - 1;
    }
    f->head = (f->head + 1) % NTAPS;

    acc >>= QSHIFT;              /* стиск Q15 назад у масштаб відліків */
    if (acc >  32767) acc =  32767;       /* насичення замість загортання */
    if (acc < -32768) acc = -32768;
    return (int16_t)acc;
}
