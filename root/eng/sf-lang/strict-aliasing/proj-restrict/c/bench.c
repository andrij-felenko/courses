// bench.c — вимір у тактах (приклад для Cortex-M з DWT->CYCCNT)
#include <stdint.h>
#include <stddef.h>

void vec_add_plain(float*, const float*, const float*, size_t);
void vec_add_restrict(float*, const float*, const float*, size_t);

// на Cortex-M лічильник тактів вмикається так:
//   CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
//   DWT->CYCCNT = 0; DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
extern volatile uint32_t* const CYCCNT;   // = &DWT->CYCCNT

#define N 4096
static float out[N], a[N], b[N];

uint32_t bench_plain(void) {
    uint32_t t0 = *CYCCNT;
    vec_add_plain(out, a, b, N);
    return *CYCCNT - t0;
}

uint32_t bench_restrict(void) {
    uint32_t t0 = *CYCCNT;
    vec_add_restrict(out, a, b, N);
    return *CYCCNT - t0;
}
