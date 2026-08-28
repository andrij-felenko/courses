#include <stdint.h>
#include <stdbool.h>

#define EMA_Q 8                  /* стільки дробових біт тримає acc */

typedef struct {
    int32_t acc;                 /* оцінка у форматі з фіксованою комою (<<Q) */
    int32_t a_num;               /* α = a_num / 256                           */
    bool    primed;
} ema_fx_t;

void ema_fx_init(ema_fx_t *f, int32_t a_num) {  /* напр. a_num=26 ≈ α 0.1 */
    f->a_num  = a_num;
    f->primed = false;
}

int32_t ema_fx_step(ema_fx_t *f, int32_t x) {
    if (!f->primed) {
        f->acc = x << EMA_Q;                 /* старт першим відліком */
        f->primed = true;
    } else {
        int32_t err = (x << EMA_Q) - f->acc; /* різниця у тому ж масштабі */
        f->acc += (f->a_num * err) >> 8;     /* + α·(x − y), знаменник 256 */
    }
    return f->acc >> EMA_Q;                   /* назовні — звичайне число */
}
