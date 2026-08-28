#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>

/* Незвідний многочлен x⁴ + x + 1 (маска 0x13 = 10011₂) для поля GF(2⁴) */
#define POLY_GF16 0x13
#define FIELD_MASK 0x0F

/* Множення двох елементів у полі GF(2⁴) */
static uint8_t gf16_mul(uint8_t a, uint8_t b) {
    uint8_t res = 0;
    a &= FIELD_MASK;
    b &= FIELD_MASK;
    while (b > 0) {
        if (b & 1) {
            res ^= a;
        }
        bool carry = (a & 0x08) != 0;
        a = (a << 1) & FIELD_MASK;
        if (carry) {
            a ^= (POLY_GF16 & FIELD_MASK);
        }
        b >>= 1;
    }
    return res;
}

/* Піднесення до квадрата у GF(2⁴) — оператор Фробеніуса для поля */
static uint8_t gf16_sqr(uint8_t a) {
    return gf16_mul(a, a);
}

/* Обернений елемент у GF(2⁴) за малою теоремою Ферма: a⁻¹ = a¹⁴ */
static uint8_t gf16_inv(uint8_t a) {
    if (a == 0) return 0;
    uint8_t a2 = gf16_sqr(a);
    uint8_t a4 = gf16_sqr(a2);
    uint8_t a8 = gf16_sqr(a4);
    /* a¹⁴ = a⁸ · a⁴ · a² */
    return gf16_mul(a8, gf16_mul(a4, a2));
}

/* Точка на кривій Кобліца y² + xy = x³ + x² + 1 над GF(2⁴) */
typedef struct {
    uint8_t x;
    uint8_t y;
    bool is_infinity;
} Point;

static const Point POINT_INFINITY = {0, 0, true};

/* Перевірка рівності двох точок */
static bool point_equals(Point p1, Point p2) {
    if (p1.is_infinity && p2.is_infinity) return true;
    if (p1.is_infinity || p2.is_infinity) return false;
    return (p1.x == p2.x) && (p1.y == p2.y);
}

/* Протилежна точка на двійковій кривій: -P = (x, x + y) */
static Point point_negate(Point p) {
    if (p.is_infinity) return p;
    Point res;
    res.x = p.x;
    res.y = p.x ^ p.y;
    res.is_infinity = false;
    return res;
}

/* Ендоморфізм Фробеніуса на точці кривої: τ(x, y) = (x², y²) */
static Point point_frobenius(Point p) {
    if (p.is_infinity) return p;
    Point res;
    res.x = gf16_sqr(p.x);
    res.y = gf16_sqr(p.y);
    res.is_infinity = false;
    return res;
}

/* Геометричне додавання двох точок на кривій Кобліца */
static Point point_add(Point p1, Point p2) {
    if (p1.is_infinity) return p2;
    if (p2.is_infinity) return p1;

    /* Випадок P1 == -P2 або P1 == P2 */
    if (p1.x == p2.x) {
        if (p1.y != p2.y || p1.x == 0) {
            return POINT_INFINITY;
        }
        /* Подвоєння точки: λ = x + y / x */
        uint8_t lambda = p1.x ^ gf16_mul(p1.y, gf16_inv(p1.x));
        uint8_t x3 = gf16_sqr(lambda) ^ lambda ^ 1; /* a = 1 */
        uint8_t y3 = gf16_mul(lambda, p1.x ^ x3) ^ x3 ^ p1.y;
        Point res = {x3, y3, false};
        return res;
    }

    /* Додавання різних точок: λ = (y1 + y2) / (x1 + x2) */
    uint8_t dx = p1.x ^ p2.x;
    uint8_t dy = p1.y ^ p2.y;
    uint8_t lambda = gf16_mul(dy, gf16_inv(dx));
    uint8_t x3 = gf16_sqr(lambda) ^ lambda ^ dx ^ 1; /* a = 1 */
    uint8_t y3 = gf16_mul(lambda, p1.x ^ x3) ^ x3 ^ p1.y;

    Point res = {x3, y3, false};
    return res;
}

/* Обчислення τ-NAF розкладу для скаляра k на кривій з μ = 1 */
static int compute_tau_naf(int k, int8_t *u_out, int max_len) {
    int r0 = k;
    int r1 = 0;
    int len = 0;
    const int mu = 1;

    while ((r0 != 0 || r1 != 0) && len < max_len) {
        if (r0 % 2 != 0) {
            int val = 2 - ((r0 - 2 * r1) % 4);
            if (val < -1) val += 4;
            if (val > 1)  val -= 4;
            u_out[len] = (int8_t)val;
            r0 -= val;
        } else {
            u_out[len] = 0;
        }
        int next_r0 = r1 + mu * (r0 / 2);
        int next_r1 = - (r0 / 2);
        r0 = next_r0;
        r1 = next_r1;
        len++;
    }
    return len;
}

/* Швидке скалярне множення через τ-NAF розклад Фробеніуса (нуль подвоєнь точок) */
static Point scalar_mul_tau_naf(Point p, int k) {
    if (k == 0 || p.is_infinity) return POINT_INFINITY;
    int8_t u[64];
    int len = compute_tau_naf(k, u, 64);

    Point q = POINT_INFINITY;
    for (int i = len - 1; i >= 0; i--) {
        q = point_frobenius(q); /* τ(Q) — піднесення координат до квадрата замість подвоєння */
        if (u[i] == 1) {
            q = point_add(q, p);
        } else if (u[i] == -1) {
            q = point_add(q, point_negate(p));
        }
    }
    return q;
}

int main(void) {
    /* Базова точка на кривій y² + xy = x³ + x² + 1 над GF(2⁴): P = (2, 8) */
    Point p = {2, 8, false};
    int k = 7;

    int8_t u[64];
    int naf_len = compute_tau_naf(k, u, 64);

    printf("Скаляр k = %d у τ-NAF поданні:\n", k);
    printf("u = [ ");
    for (int i = naf_len - 1; i >= 0; i--) {
        printf("%d ", u[i]);
    }
    printf("] (довжина розкладу: %d)\n", naf_len);

    Point res = scalar_mul_tau_naf(p, k);
    printf("Результат скалярного множення %d · P = (%d, %d)\n", k, res.x, res.y);

    return 0;
}
