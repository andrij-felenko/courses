#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>

/* Опис структури звичайного дробу */
typedef struct {
    int64_t num; /* Чисельник зі знаком */
    int64_t den; /* Знаменник (завжди > 0) */
} rational_t;

/* Алгоритм Евкліда для 64-бітних цілих чисел */
static int64_t gcd_i64(int64_t a, int64_t b) {
    a = a < 0 ? -a : a;
    b = b < 0 ? -b : b;
    while (b != 0) {
        int64_t temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

/* Нормалізація дробу: приведення знаменника до додатного та скорочення через НСД */
static rational_t rational_make(int64_t num, int64_t den, bool *ok) {
    if (den == 0) {
        if (ok) *ok = false;
        rational_t err = {0, 1};
        return err;
    }
    if (ok) *ok = true;

    if (den < 0) {
        num = -num;
        den = -den;
    }

    int64_t g = gcd_i64(num, den);
    rational_t r = { num / g, den / g };
    return r;
}

/* Додавання дробів: a/b + c/d через найменший спільний знаменник */
rational_t rational_add(rational_t r1, rational_t r2, bool *ok) {
    int64_t g = gcd_i64(r1.den, r2.den);
    int64_t b_prime = r1.den / g;
    int64_t d_prime = r2.den / g;

    int64_t num = r1.num * d_prime + r2.num * b_prime;
    int64_t den = r1.den * d_prime;

    return rational_make(num, den, ok);
}

/* Віднімання дробів: a/b - c/d */
rational_t rational_sub(rational_t r1, rational_t r2, bool *ok) {
    rational_t neg_r2 = { -r2.num, r2.den };
    return rational_add(r1, neg_r2, ok);
}

/* Множення дробів зі скороченням нахрест */
rational_t rational_mul(rational_t r1, rational_t r2, bool *ok) {
    int64_t g1 = gcd_i64(r1.num, r2.den);
    int64_t g2 = gcd_i64(r2.num, r1.den);

    int64_t num = (r1.num / g1) * (r2.num / g2);
    int64_t den = (r1.den / g2) * (r2.den / g1);

    return rational_make(num, den, ok);
}

/* Ділення дробів: (a/b) / (c/d) = (a/b) * (d/c) */
rational_t rational_div(rational_t r1, rational_t r2, bool *ok) {
    if (r2.num == 0) {
        if (ok) *ok = false;
        rational_t err = {0, 1};
        return err;
    }
    rational_t inv_r2 = { r2.den, r2.num };
    return rational_mul(r1, inv_r2, ok);
}

void rational_print(rational_t r) {
    if (r.den == 1) {
        printf("%lld", (long long)r.num);
    } else {
        printf("%lld/%lld", (long long)r.num, (long long)r.den);
    }
}

int main(void) {
    bool ok = false;
    rational_t a = rational_make(7, 12, &ok);
    rational_t b = rational_make(5, 18, &ok);

    rational_t sum = rational_add(a, b, &ok);
    printf("7/12 + 5/18 = ");
    rational_print(sum);
    printf("\n");

    rational_t prod = rational_mul(a, b, &ok);
    printf("7/12 * 5/18 = ");
    rational_print(prod);
    printf("\n");

    return 0;
}
