#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* Структура попередньо обчислених параметрів RSA-CRT для фіксованої розрядності */
typedef struct {
    const uint64_t *p;       /* Простий дільник p (1024 біти / 16 слів по 64 біти) */
    const uint64_t *q;       /* Простий дільник q (1024 біти) */
    const uint64_t *dp;      /* d_p = d mod (p - 1) */
    const uint64_t *dq;      /* d_q = d mod (q - 1) */
    const uint64_t *qinv;    /* q_inv = q^(-1) mod p */
    size_t limbs_half;       /* Кількість 64-бітних слів у p та q (наприклад, 16) */
} rsa_crt_key_t;

/* Прототипи модульної арифметики великих чисел (BigInt) */
void bigint_mod_exp(uint64_t *res, const uint64_t *base, const uint64_t *exp,
                    const uint64_t *mod, size_t len);
void bigint_sub_mod(uint64_t *res, const uint64_t *a, const uint64_t *b,
                    const uint64_t *mod, size_t len);
void bigint_mul_mod(uint64_t *res, const uint64_t *a, const uint64_t *b,
                    const uint64_t *mod, size_t len);
void bigint_mul_add(uint64_t *res, const uint64_t *m_q, const uint64_t *h,
                    const uint64_t *q, size_t len_half);

/* Виконання розшифрування за схемою RSA-CRT за алгоритмом Гарнера */
bool rsa_crt_decrypt(uint64_t *out_m, const uint64_t *in_c, const rsa_crt_key_t *key) {
    size_t n = key->limbs_half;
    uint64_t mp[32]; /* Буфер для 1024-бітного проміжного результату */
    uint64_t mq[32];
    uint64_t h[32];
    uint64_t diff[32];

    if (n > 32) return false;

    /* 1. Паралельне обчислення частин повідомлення у факторах p та q */
    bigint_mod_exp(mp, in_c, key->dp, key->p, n);
    bigint_mod_exp(mq, in_c, key->dq, key->q, n);

    /* 2. Обчислення h = (q_inv * (m_p - m_q)) mod p */
    bigint_sub_mod(diff, mp, mq, key->p, n);
    bigint_mul_mod(h, diff, key->qinv, key->p, n);

    /* 3. Фінальна реконструкція Garner: m = m_q + h * q (результат 2048 бітів) */
    bigint_mul_add(out_m, mq, h, key->q, n);

    return true;
}
