#include <stdint.h>
#include <stdbool.h>

/* Точний цілочисельний квадратний корінь на регістрах ALU */
static inline uint64_t isqrt64(uint64_t n) {
    if (n == 0) return 0;
    uint64_t root = 0;
    uint64_t bit = (uint64_t)1 << 62;

    while (bit > n) {
        bit >>= 2;
    }
    while (bit != 0) {
        if (n >= root + bit) {
            n -= root + bit;
            root = (root >> 1) + bit;
        } else {
            root >>= 1;
        }
        bit >>= 2;
    }
    return root;
}

/* Безпечне пряме кодування пари 32-бітних координат */
bool cantor_encode(uint32_t x, uint32_t y, uint64_t *out_code) {
    if (!out_code) return false;
    uint64_t ux = (uint64_t)x;
    uint64_t uy = (uint64_t)y;
    uint64_t w = ux + uy;

    if (w > 6074000999ULL) return false; /* Захист від переповнення uint64 */

    *out_code = (w * (w + 1)) / 2 + uy;
    return true;
}

/* Точне аналітичне розпакування 64-бітного коду Кантора */
bool cantor_decode(uint64_t code, uint32_t *out_x, uint32_t *out_y) {
    if (!out_x || !out_y) return false;

    #if defined(__SIZEOF_INT128__)
        unsigned __int128 disc = ((unsigned __int128)code * 8) + 1;
        uint64_t s;
        if (disc <= UINT64_MAX) {
            s = isqrt64((uint64_t)disc);
        } else {
            unsigned __int128 r = 0, b = (unsigned __int128)1 << 126;
            while (b > disc) b >>= 2;
            while (b != 0) {
                if (disc >= r + b) { disc -= r + b; r = (r >> 1) + b; }
                else { r >>= 1; }
                b >>= 2;
            }
            s = (uint64_t)r;
        }
    #else
        if (code >= (UINT64_MAX / 8)) return false;
        uint64_t s = isqrt64(8 * code + 1);
    #endif

    uint64_t w = (s - 1) / 2;
    uint64_t base = (w * (w + 1)) / 2;
    uint64_t y = code - base;
    uint64_t x = w - y;

    if (x > UINT32_MAX || y > UINT32_MAX) return false;

    *out_x = (uint32_t)x;
    *out_y = (uint32_t)y;
    return true;
}
