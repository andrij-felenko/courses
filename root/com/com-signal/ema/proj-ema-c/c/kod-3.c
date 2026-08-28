#include <stdint.h>
#include <stdbool.h>

#define EMA_SHIFT 3          /* α = 1/2^SHIFT (SHIFT=3 → α = 1/8) */
#define EMA_Q     8          /* стільки дробових біт тримає acc    */

typedef struct {
    int32_t acc;             /* оцінка у форматі з фіксованою комою (<<Q) */
    bool    primed;
} ema_pow2_t;

int32_t ema_pow2_step(ema_pow2_t *f, int32_t x) {
    if (!f->primed) {
        f->acc = x << EMA_Q;                 /* старт першим відліком */
        f->primed = true;
    } else {
        int32_t err = (x << EMA_Q) - f->acc; /* різниця у тому ж масштабі */
        f->acc += err >> EMA_SHIFT;          /* α·(x − y) — самий зсув, без множення */
    }
    return f->acc >> EMA_Q;                   /* назовні — звичайне число */
}
