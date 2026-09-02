#include "fixedq16.h"

int32_t sat_from_i64(int64_t v) {
    if (v > (int64_t)INT32_MAX) {
        return INT32_MAX;
    }
    if (v < (int64_t)INT32_MIN) {
        return INT32_MIN;
    }
    return (int32_t)v;
}

int32_t sat_add_i32(int32_t a, int32_t b) {
    /* Рахуємо у 64 бітах: знакове переповнення int32 — невизначена поведінка,
       компілятор має право викинути будь-яку перевірку ПІСЛЯ додавання. */
    return sat_from_i64((int64_t)a + (int64_t)b);
}

int32_t sat_sub_i32(int32_t a, int32_t b) {
    return sat_from_i64((int64_t)a - (int64_t)b);
}

int32_t sat_bits(int32_t v, unsigned bits) {
    if (bits == 0u || bits >= 32u) {
        return v; /* обмежувати нічим */
    }
    {
        const int32_t hi = ((int32_t)1 << (bits - 1u)) - 1;
        const int32_t lo = -((int32_t)1 << (bits - 1u));
        if (v > hi) {
            return hi;
        }
        if (v < lo) {
            return lo;
        }
        return v;
    }
}

int16_t sat_to_i16(int32_t v) {
#if defined(__ARM_ARCH) && (__ARM_ARCH >= 7)
    /* SSAT обмежує 32-бітне знакове число 16 розрядами за один такт. */
    int32_t r;
    __asm__("ssat %0, #16, %1" : "=r"(r) : "r"(v));
    return (int16_t)r;
#else
    return (int16_t)sat_bits(v, 16u);
#endif
}

int32_t q16_from_int(int32_t v) {
    /* Ціла частина Q16.16 — лише 15 бітів плюс знак. */
    if (v > 32767) {
        return INT32_MAX;
    }
    if (v < -32768) {
        return INT32_MIN;
    }
    return v * Q16_ONE;
}

int32_t q16_to_int(int32_t q) {
    /* Симетричне округлення: зсув праворуч округлює донизу, тому для
       від'ємних чисел додаємо половину ваги LSB з від'ємним знаком. */
    const int64_t bias = (q >= 0) ? (int64_t)Q16_HALF : -(int64_t)Q16_HALF;
    return (int32_t)(((int64_t)q + bias) >> Q16_FRAC);
}

int32_t q16_mul(int32_t a, int32_t b) {
    const int64_t prod = (int64_t)a * (int64_t)b; /* SMULL: 1 такт на M3/M4 */
    const int64_t bias = (prod >= 0) ? (int64_t)Q16_HALF : -(int64_t)Q16_HALF;
    return sat_from_i64((prod + bias) >> Q16_FRAC);
}

int32_t q16_div(int32_t a, int32_t b) {
    if (b == 0) {
        /* Прошивку не спиняємо: контур керування дістає межу діапазону
           з правильним знаком, а не виняток і не нуль. */
        return (a >= 0) ? INT32_MAX : INT32_MIN;
    }
    {
        /* Зсуваємо ділене вліво на кількість дробових бітів дільника —
           інакше частка втратила б усю дробову частину. */
        int64_t num = (int64_t)a << Q16_FRAC;
        const int64_t half = (b >= 0) ? ((int64_t)b / 2) : (-(int64_t)b / 2);
        num += (num >= 0) ? half : -half;
        /* INT32_MIN / -1 не влазить у 32 біти — насичення це ловить. */
        return sat_from_i64(num / (int64_t)b);
    }
}

int32_t q16_scale_raw(int16_t raw, int16_t zero, int32_t w_q16) {
    /* Різниця двох int16 не влазить в int16 (-32768 - 32767), тому 32 біти. */
    const int32_t centred = (int32_t)raw - (int32_t)zero;
    const int64_t prod = (int64_t)centred * (int64_t)w_q16;
    const int64_t bias = (prod >= 0) ? (int64_t)Q16_HALF : -(int64_t)Q16_HALF;
    return sat_from_i64((prod + bias) >> Q16_FRAC);
}

uint32_t u64_isqrt(uint64_t v) {
    if (v == 0u) {
        return 0u;
    }
    {
        /* Метод Герона на цілих: три-чотири ітерації для типових величин. */
        uint64_t x = v;
        uint64_t y = 1u;
        while (x > y) {
            x = (x + y) / 2u;
            y = v / x;
        }
        return (uint32_t)x;
    }
}
