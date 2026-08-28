#include <stdint.h>
#include <string.h>

typedef uint32_t limb;                 /* слово 32 біти; добуток двох влазить у 64 */

/* довжина числа в бітах (номер старшого одиничного біта) */
static int bit_length(const limb *a, int words) {
    for (int i = words - 1; i >= 0; i--)
        if (a[i]) { int b = 32; while (!((a[i] >> (b - 1)) & 1u)) b--; return 32 * i + b; }
    return 0;
}

/* out[0..n) = a[0..W) >> p */
static void shift_right_p(const limb *a, int W, int p, limb *out, int n) {
    int Q = p / 32, R = p % 32;                 /* R ∈ [1,31] */
    for (int i = 0; i < n; i++) {
        uint64_t lo = (i + Q     < W) ? a[i + Q]     : 0;
        uint64_t hi = (i + Q + 1 < W) ? a[i + Q + 1] : 0;
        out[i] = (limb)((lo >> R) | (hi << (32 - R)));
    }
}

/* a[0..W) += b[0..W) */
static void add_inplace(limb *a, const limb *b, int W) {
    uint64_t carry = 0;
    for (int i = 0; i < W; i++) {
        uint64_t cur = (uint64_t)a[i] + b[i] + carry;
        a[i] = (limb)cur;
        carry = cur >> 32;
    }
}

/* ⋆ серце всього ⋆   r[0..n) = prod[0..2n) mod (2ᵖ − 1),  жодного ділення */
static void reduce_mod_mp(const limb *prod, int p, limb *r, int n) {
    int W = 2 * n, Q = p / 32, R = p % 32;
    limb acc[W], low[W], high[W];               /* C99 VLA — для наочності */
    memcpy(acc, prod, W * sizeof(limb));
    while (bit_length(acc, W) > p) {            /* доки згори лишаються біти */
        for (int i = 0; i < W; i++)            /* low = acc & (2ᵖ − 1) */
            low[i] = (i < Q) ? acc[i] : (i == Q ? (acc[i] & ((1u << R) - 1)) : 0);
        shift_right_p(acc, W, p, high, W);     /* high = acc >> p */
        memset(acc, 0, W * sizeof(limb));
        add_inplace(acc, low, W);
        add_inplace(acc, high, W);             /* acc = low + high — згортка */
    }
    for (int i = 0; i < n; i++) r[i] = acc[i];
    int is_mp = 1;                              /* остача == Mp (усі одиниці)? */
    for (int i = 0; i < n - 1; i++) if (r[i] != 0xFFFFFFFFu) is_mp = 0;
    if (r[n - 1] != (1u << R) - 1) is_mp = 0;
    if (is_mp) memset(r, 0, n * sizeof(limb));  /* … значить нуль */
}
