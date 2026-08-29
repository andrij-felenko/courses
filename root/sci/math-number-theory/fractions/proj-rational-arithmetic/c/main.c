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

/* Статус виконання операцій */
typedef enum {
    RATIONAL_OK = 0,
    RATIONAL_ERR_ZERO_DENOMINATOR = 1,
    RATIONAL_ERR_DIV_BY_ZERO = 2
} rational_status_t;

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
rational_t rational_make(int64_t num, int64_t den, rational_status_t *status) {
    if (den == 0) {
        if (status) *status = RATIONAL_ERR_ZERO_DENOMINATOR;
        rational_t err = {0, 1};
        return err;
    }
    if (status) *status = RATIONAL_OK;

    if (den < 0) {
        num = -num;
        den = -den;
    }

    int64_t g = gcd_i64(num, den);
    rational_t r = { num / g, den / g };
    return r;
}

/* Унарний мінус: -r */
rational_t rational_neg(rational_t r) {
    rational_t res = { -r.num, r.den };
    return res;
}

/* Абсолютна величина: |r| */
rational_t rational_abs(rational_t r) {
    rational_t res = { r.num < 0 ? -r.num : r.num, r.den };
    return res;
}

/* Додавання дробів: a/b + c/d через найменший спільний знаменник */
rational_t rational_add(rational_t r1, rational_t r2, rational_status_t *status) {
    int64_t g = gcd_i64(r1.den, r2.den);
    int64_t b_prime = r1.den / g;
    int64_t d_prime = r2.den / g;

    int64_t num = r1.num * d_prime + r2.num * b_prime;
    int64_t den = r1.den * d_prime;

    return rational_make(num, den, status);
}

/* Віднімання дробів: a/b - c/d */
rational_t rational_sub(rational_t r1, rational_t r2, rational_status_t *status) {
    return rational_add(r1, rational_neg(r2), status);
}

/* Множення дробів зі скороченням нахрест */
rational_t rational_mul(rational_t r1, rational_t r2, rational_status_t *status) {
    int64_t g1 = gcd_i64(r1.num, r2.den);
    int64_t g2 = gcd_i64(r2.num, r1.den);

    int64_t num = (r1.num / g1) * (r2.num / g2);
    int64_t den = (r1.den / g2) * (r2.den / g1);

    return rational_make(num, den, status);
}

/* Ділення дробів: (a/b) / (c/d) = (a/b) * (d/c) */
rational_t rational_div(rational_t r1, rational_t r2, rational_status_t *status) {
    if (r2.num == 0) {
        if (status) *status = RATIONAL_ERR_DIV_BY_ZERO;
        rational_t err = {0, 1};
        return err;
    }
    rational_t inv_r2 = { r2.den, r2.num };
    return rational_mul(r1, inv_r2, status);
}

/* Піднесення до цілого степеня: r^exp */
rational_t rational_pow(rational_t r, int exp, rational_status_t *status) {
    if (exp == 0) {
        return rational_make(1, 1, status);
    }
    if (exp < 0) {
        if (r.num == 0) {
            if (status) *status = RATIONAL_ERR_DIV_BY_ZERO;
            rational_t err = {0, 1};
            return err;
        }
        rational_t inv = { r.den, r.num };
        return rational_pow(inv, -exp, status);
    }

    int64_t base_num = r.num;
    int64_t base_den = r.den;
    int64_t res_num = 1;
    int64_t res_den = 1;

    while (exp > 0) {
        if (exp % 2 == 1) {
            res_num *= base_num;
            res_den *= base_den;
        }
        base_num *= base_num;
        base_den *= base_den;
        exp /= 2;
    }

    return rational_make(res_num, res_den, status);
}

/* Безпечне порівняння дробів без 64-бітного переповнення: повертає -1, 0, 1 */
int rational_compare(rational_t r1, rational_t r2) {
    if (r1.num == r2.num && r1.den == r2.den) return 0;

    int64_t s1 = r1.num < 0 ? -1 : (r1.num > 0 ? 1 : 0);
    int64_t s2 = r2.num < 0 ? -1 : (r2.num > 0 ? 1 : 0);
    if (s1 != s2) return (s1 < s2) ? -1 : 1;
    if (s1 == 0) return 0;

    int64_t a = r1.num < 0 ? -r1.num : r1.num;
    int64_t b = r1.den;
    int64_t c = r2.num < 0 ? -r2.num : r2.num;
    int64_t d = r2.den;

    while (true) {
        int64_t q1 = a / b;
        int64_t q2 = c / d;
        if (q1 != q2) {
            int cmp = (q1 < q2) ? -1 : 1;
            return (s1 > 0) ? cmp : -cmp;
        }
        int64_t rem1 = a % b;
        int64_t rem2 = c % d;
        if (rem1 == 0 || rem2 == 0) {
            if (rem1 == 0 && rem2 == 0) return 0;
            int cmp = (rem1 == 0) ? -1 : 1;
            return (s1 > 0) ? cmp : -cmp;
        }
        a = d;
        b = rem2;
        c = b;
        d = rem1;
    }
}

/* Перетворення у число з плаваючою крапкою double */
double rational_to_double(rational_t r) {
    return (double)r.num / (double)r.den;
}

/* Друк звичайного дробу у консоль */
void rational_print(rational_t r) {
    if (r.den == 1) {
        printf("%lld", (long long)r.num);
    } else {
        printf("%lld/%lld", (long long)r.num, (long long)r.den);
    }
}

int main(void) {
    rational_status_t status = RATIONAL_OK;
    rational_t a = rational_make(7, 12, &status);
    rational_t b = rational_make(5, 18, &status);

    printf("--- Тестування раціональної арифметики мовою C ---\n");
    printf("a = "); rational_print(a); printf(", b = "); rational_print(b); printf("\n");

    rational_t sum = rational_add(a, b, &status);
    printf("a + b = "); rational_print(sum); printf(" (очікувано 31/36)\n");

    rational_t diff = rational_sub(a, b, &status);
    printf("a - b = "); rational_print(diff); printf(" (очікувано 11/36)\n");

    rational_t prod = rational_mul(a, b, &status);
    printf("a * b = "); rational_print(prod); printf(" (очікувано 35/216)\n");

    rational_t quot = rational_div(a, b, &status);
    printf("a / b = "); rational_print(quot); printf(" (очікувано 21/10)\n");

    rational_t p2 = rational_pow(rational_make(2, 3, &status), 3, &status);
    printf("(2/3)^3 = "); rational_print(p2); printf(" (очікувано 8/27)\n");

    rational_t p_neg = rational_pow(rational_make(2, 3, &status), -2, &status);
    printf("(2/3)^(-2) = "); rational_print(p_neg); printf(" (очікувано 9/4)\n");

    int cmp = rational_compare(a, b);
    printf("Порівняння a та b: %s\n", cmp > 0 ? "a > b" : (cmp < 0 ? "a < b" : "a == b"));

    rational_t bad = rational_make(5, 0, &status);
    if (status == RATIONAL_ERR_ZERO_DENOMINATOR) {
        printf("Успішно перехоплено нульовий знаменник!\n");
    }

    return 0;
}
