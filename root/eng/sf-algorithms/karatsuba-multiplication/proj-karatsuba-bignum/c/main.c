#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>

#define KARATSUBA_THRESHOLD 32

/* Базове множення у стовпчик O(n^2) для малого розміру n */
void schoolbook_mul(const uint32_t *a, const uint32_t *b, uint32_t *out, size_t n) {
    memset(out, 0, 2 * n * sizeof(uint32_t));
    for (size_t i = 0; i < n; ++i) {
        if (a[i] == 0) continue;
        uint64_t carry = 0;
        for (size_t j = 0; j < n; ++j) {
            uint64_t cur = (uint64_t)out[i + j] + (uint64_t)a[i] * (uint64_t)b[j] + carry;
            out[i + j] = (uint32_t)cur;
            carry = cur >> 32;
        }
        out[i + n] += (uint32_t)carry;
    }
}

/* Додавання двох масивів довжини n з поверненням біта перенесення */
uint32_t bignum_add_n(const uint32_t *a, const uint32_t *b, uint32_t *out, size_t n) {
    uint64_t carry = 0;
    for (size_t i = 0; i < n; ++i) {
        uint64_t sum = (uint64_t)a[i] + (uint64_t)b[i] + carry;
        out[i] = (uint32_t)sum;
        carry = sum >> 32;
    }
    return (uint32_t)carry;
}

/* Віднімання bignum: a - b, повертає запозичення (borrow: 0 або 1) */
uint32_t bignum_sub_n(const uint32_t *a, const uint32_t *b, uint32_t *out, size_t n) {
    int64_t borrow = 0;
    for (size_t i = 0; i < n; ++i) {
        int64_t diff = (int64_t)a[i] - (int64_t)b[i] - borrow;
        if (diff < 0) {
            out[i] = (uint32_t)(diff + 0x100000000ULL);
            borrow = 1;
        } else {
            out[i] = (uint32_t)diff;
            borrow = 0;
        }
    }
    return (uint32_t)borrow;
}

/* Додавання до акумулятора з позиції offset */
void bignum_add_offset(uint32_t *dst, const uint32_t *src, size_t n, size_t offset, size_t dst_len) {
    uint64_t carry = 0;
    for (size_t i = 0; i < n && (offset + i) < dst_len; ++i) {
        uint64_t sum = (uint64_t)dst[offset + i] + (uint64_t)src[i] + carry;
        dst[offset + i] = (uint32_t)sum;
        carry = sum >> 32;
    }
    for (size_t i = offset + n; carry != 0 && i < dst_len; ++i) {
        uint64_t sum = (uint64_t)dst[i] + carry;
        dst[i] = (uint32_t)sum;
        carry = sum >> 32;
    }
}

/* Рекурсивне множення Карацуби зі скретчпадом */
void karatsuba_rec(const uint32_t *a, const uint32_t *b, uint32_t *out, size_t n, uint32_t *scratch) {
    if (n <= KARATSUBA_THRESHOLD) {
        schoolbook_mul(a, b, out, n);
        return;
    }

    size_t m = n / 2;
    const uint32_t *a_l = a;
    const uint32_t *a_h = a + m;
    const uint32_t *b_l = b;
    const uint32_t *b_h = b + m;

    uint32_t *z0 = out;
    uint32_t *z2 = out + 2 * m;

    /* Робоча пам'ять:
       scratch[0 .. 2m-1] -> z_mid
       scratch[2m .. 3m-1] -> sum_a (m лімбів)
       scratch[3m .. 4m-1] -> sum_b (m лімбів)
       scratch[4m .. ] -> вкладений скретчпад для рекурсії */
    uint32_t *z_mid = scratch;
    uint32_t *sum_a = scratch + 2 * m;
    uint32_t *sum_b = scratch + 3 * m;
    uint32_t *sub_scratch = scratch + 4 * m;

    /* 1. Обчислення Z0 = a_l * b_l */
    karatsuba_rec(a_l, b_l, z0, m, sub_scratch);

    /* 2. Обчислення Z2 = a_h * b_h */
    karatsuba_rec(a_h, b_h, z2, m, sub_scratch);

    /* 3. Формування сум половин */
    uint32_t carry_a = bignum_add_n(a_l, a_h, sum_a, m);
    uint32_t carry_b = bignum_add_n(b_l, b_h, sum_b, m);

    /* 4. Обчислення Z_mid = (a_l + a_h) * (b_l + b_h) */
    karatsuba_rec(sum_a, sum_b, z_mid, m, sub_scratch);

    /* Корекція Z_mid для старших бітів перенесення carry_a та carry_b */
    if (carry_a) bignum_add_offset(z_mid, sum_b, m, m, 2 * m);
    if (carry_b) bignum_add_offset(z_mid, sum_a, m, m, 2 * m);

    /* 5. Z1 = Z_mid - Z0 - Z2 */
    bignum_sub_n(z_mid, z0, z_mid, 2 * m);
    bignum_sub_n(z_mid, z2, z_mid, 2 * m);

    /* 6. Додавання Z1 зі зсувом на m слів */
    bignum_add_offset(out, z_mid, 2 * m, m, 2 * n);
}
