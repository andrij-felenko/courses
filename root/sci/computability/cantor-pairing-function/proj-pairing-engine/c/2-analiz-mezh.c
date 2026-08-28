/* Структура для повернення пари 32-бітних координат */
typedef struct {
    uint32_t x;
    uint32_t y;
} cantor_pair32_t;

/* Структура для повернення пари 64-бітних координат */
typedef struct {
    uint64_t x;
    uint64_t y;
} cantor_pair64_t;

/* Безпечне кодування двох 32-бітних чисел у 64-бітний індекс Кантора.
   Повертає true у разі успіху, або false при переповненні uint64_t. */
bool cantor_encode32(uint32_t x, uint32_t y, uint64_t *out_code) {
    if (!out_code) return false;

    uint64_t u_x = (uint64_t)x;
    uint64_t u_y = (uint64_t)y;
    uint64_t w = u_x + u_y;

    /* Поріг переповнення uint64_t для формули w*(w+1)/2 */
    if (w > 6074000999ULL) {
        return false;
    }

    uint64_t base = (w * (w + 1)) / 2;
    *out_code = base + u_y;
    return true;
}

/* Декодування 64-бітного індексу Кантора у пару 32-бітних координат.
   Використовує 128-бітне розширення для безпеки обчислення 8*code + 1. */
bool cantor_decode32(uint64_t code, cantor_pair32_t *out_pair) {
    if (!out_pair) return false;

    #if defined(__SIZEOF_INT128__)
        unsigned __int128 disc = ((unsigned __int128)code * 8) + 1;
        uint64_t s;
        if (disc <= UINT64_MAX) {
            s = isqrt64_fast((uint64_t)disc);
        } else {
            /* 128-бітний алгоритм добування кореня для великих значень */
            unsigned __int128 r = 0, b = (unsigned __int128)1 << 126;
            while (b > disc) b >>= 2;
            while (b != 0) {
                if (disc >= r + b) {
                    disc -= r + b;
                    r = (r >> 1) + b;
                } else {
                    r >>= 1;
                }
                b >>= 2;
            }
            s = (uint64_t)r;
        }
    #else
        if (code >= (UINT64_MAX / 8)) return false;
        uint64_t s = isqrt64_fast(8 * code + 1);
    #endif

    uint64_t w = (s - 1) / 2;
    uint64_t base = (w * (w + 1)) / 2;
    uint64_t y = code - base;
    uint64_t x = w - y;

    if (x > UINT32_MAX || y > UINT32_MAX) {
        return false;
    }

    out_pair->x = (uint32_t)x;
    out_pair->y = (uint32_t)y;
    return true;
}
