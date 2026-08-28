#include <stdint.h>
#include <stdlib.h>
#include <math.h>

/* Простий відтворюваний ГПВЧ (xorshift32): один seed → один і той самий
   поділ. Відтворюваність тут не примха: та сама розбивка потрібна, щоб
   чесно порівнювати дві моделі на однакових блоках, і щоб баг можна було
   відтворити. rand() із libc для цього гірший — його якість і період
   залежать від платформи. */
static uint32_t rng_state;

static void rng_seed(uint32_t s) {
    rng_state = s ? s : 0x1234567u;   /* нуль зациклив би xorshift на нулі */
}

static uint32_t rng_next(void) {
    uint32_t x = rng_state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    rng_state = x;
    return x;
}

/* Рівномірне ціле в [0, m) без модуло-зсуву:
   наївне rng_next() % m трохи частішає малі залишки, коли 2³² не кратне m.
   Відкидаємо «хвіст», що псує рівномірність. */
static uint32_t rng_below(uint32_t m) {
    uint32_t limit = UINT32_MAX - (UINT32_MAX % m);   /* найбільше кратне m */
    uint32_t r;
    do { r = rng_next(); } while (r >= limit);
    return r % m;
}

/* Перемішати order[0..n-1] на місці (Фішер–Єйтс, прохід із кінця). */
static void shuffle(int *order, int n) {
    for (int i = n - 1; i > 0; i--) {
        uint32_t j = rng_below((uint32_t)(i + 1));   /* j ∈ [0, i] включно */
        int t = order[i]; order[i] = order[j]; order[j] = t;
    }
}
