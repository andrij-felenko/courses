#include <stdint.h>
#include <stddef.h>
#include <string.h>

#define KARATSUBA_THRESHOLD 32

/* Базовий шкільний стовпчик для малих розмірів */
static void schoolbook_multiply(const uint32_t *a, const uint32_t *b, uint32_t *out, size_t n) {
    memset(out, 0, 2 * n * sizeof(uint32_t));
    for (size_t i = 0; i < n; ++i) {
        if (a[i] == 0) continue;
        uint64_t carry = 0;
        for (size_t j = 0; j < n; ++j) {
            uint64_t prod = (uint64_t)out[i + j] + (uint64_t)a[i] * (uint64_t)b[j] + carry;
            out[i + j] = (uint32_t)prod;
            carry = prod >> 32;
        }
        out[i + n] += (uint32_t)carry;
    }
}

/* Додавання векторів однакової довжини з поверненням перенесення */
static uint32_t add_limbs(const uint32_t *a, const uint32_t *b, uint32_t *out, size_t n) {
    uint64_t carry = 0;
    for (size_t i = 0; i < n; ++i) {
        uint64_t sum = (uint64_t)a[i] + (uint64_t)b[i] + carry;
        out[i] = (uint32_t)sum;
        carry = sum >> 32;
    }
    return (uint32_t)carry;
}

/* Віднімання векторів: out = a - b, повертає запозичення */
static uint32_t sub_limbs(uint32_t *a, const uint32_t *b, size_t n) {
    int64_t borrow = 0;
    for (size_t i = 0; i < n; ++i) {
        int64_t diff = (int64_t)a[i] - (int64_t)b[i] - borrow;
        if (diff < 0) {
            a[i] = (uint32_t)(diff + 0x100000000ULL);
            borrow = 1;
        } else {
            a[i] = (uint32_t)diff;
            borrow = 0;
        }
    }
    return (uint32_t)borrow;
}

/* Додавання з позиційним зсувом */
static void add_with_offset(uint32_t *dst, const uint32_t *src, size_t n, size_t offset, size_t dst_len) {
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

/* Головне рекурсивне ядро Карацуби */
void karatsuba_multiply_core(const uint32_t *a, const uint32_t *b, uint32_t *out, size_t n, uint32_t *scratch) {
    if (n <= KARATSUBA_THRESHOLD) {
        schoolbook_multiply(a, b, out, n);
        return;
    }

    size_t m = n / 2;
    const uint32_t *a_l = a;
    const uint32_t *a_h = a + m;
    const uint32_t *b_l = b;
    const uint32_t *b_h = b + m;

    uint32_t *z0 = out;
    uint32_t *z2 = out + 2 * m;

    uint32_t *z_mid = scratch;
    uint32_t *sum_a = scratch + 2 * m;
    uint32_t *sum_b = scratch + 3 * m;
    uint32_t *nested_scratch = scratch + 4 * m;

    /* 1. Обчислюємо Z0 = a_l * b_l */
    karatsuba_multiply_core(a_l, b_l, z0, m, nested_scratch);

    /* 2. Обчислюємо Z2 = a_h * b_h */
    karatsuba_multiply_core(a_h, b_h, z2, m, nested_scratch);

    /* 3. Формуємо суми половин */
    uint32_t carry_a = add_limbs(a_l, a_h, sum_a, m);
    uint32_t carry_b = add_limbs(b_l, b_h, sum_b, m);

    /* 4. Обчислюємо Z_mid = (a_l + a_h) * (b_l + b_h) */
    karatsuba_multiply_core(sum_a, sum_b, z_mid, m, nested_scratch);

    /* Корекція старших перенесень для Z_mid */
    if (carry_a) add_with_offset(z_mid, sum_b, m, m, 2 * m);
    if (carry_b) add_with_offset(z_mid, sum_a, m, m, 2 * m);

    /* 5. Z1 = Z_mid - Z0 - Z2 */
    sub_limbs(z_mid, z0, 2 * m);
    sub_limbs(z_mid, z2, 2 * m);

    /* 6. Акумулюємо Z1 у фінальний результат зі зсувом на m слів */
    add_with_offset(out, z_mid, 2 * m, m, 2 * n);
}
