#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define MAX_DEG 128

/* Структура для представлення многочлена над F_p */
typedef struct {
    int deg;
    int c[MAX_DEG + 1]; /* c[i] - коефіцієнт при x^i */
} Poly;

/* Нормалізація степеня многочлена */
static void poly_normalize(Poly *p, int mod) {
    for (int i = 0; i <= p->deg; i++) {
        p->c[i] = (p->c[i] % mod + mod) % mod;
    }
    while (p->deg > 0 && p->c[p->deg] == 0) {
        p->deg--;
    }
}

/* Ініціалізація нульового многочлена */
static Poly poly_zero(void) {
    Poly p;
    p.deg = 0;
    memset(p.c, 0, sizeof(p.c));
    return p;
}

/* Додавання многочленів над F_p */
static Poly poly_add(const Poly *a, const Poly *b, int mod) {
    Poly r = poly_zero();
    r.deg = (a->deg > b->deg) ? a->deg : b->deg;
    for (int i = 0; i <= r.deg; i++) {
        int ca = (i <= a->deg) ? a->c[i] : 0;
        int cb = (i <= b->deg) ? b->c[i] : 0;
        r.c[i] = (ca + cb) % mod;
    }
    poly_normalize(&r, mod);
    return r;
}

/* Віднімання многочленів над F_p */
static Poly poly_sub(const Poly *a, const Poly *b, int mod) {
    Poly r = poly_zero();
    r.deg = (a->deg > b->deg) ? a->deg : b->deg;
    for (int i = 0; i <= r.deg; i++) {
        int ca = (i <= a->deg) ? a->c[i] : 0;
        int cb = (i <= b->deg) ? b->c[i] : 0;
        r.c[i] = (ca - cb + mod) % mod;
    }
    poly_normalize(&r, mod);
    return r;
}

/* Обернений елемент у полі F_p за малою теоремою Ферма */
static int mod_inv(int a, int mod) {
    a = (a % mod + mod) % mod;
    int res = 1, base = a, exp = mod - 2;
    while (exp > 0) {
        if (exp & 1) res = (res * base) % mod;
        base = (base * base) % mod;
        exp >>= 1;
    }
    return res;
}

/* Множення многочленів над F_p */
static Poly poly_mul(const Poly *a, const Poly *b, int mod) {
    Poly r = poly_zero();
    if ((a->deg == 0 && a->c[0] == 0) || (b->deg == 0 && b->c[0] == 0)) {
        return r;
    }
    r.deg = a->deg + b->deg;
    if (r.deg > MAX_DEG) r.deg = MAX_DEG;
    for (int i = 0; i <= a->deg; i++) {
        for (int j = 0; j <= b->deg && (i + j) <= MAX_DEG; j++) {
            r.c[i + j] = (r.c[i + j] + a->c[i] * b->c[j]) % mod;
        }
    }
    poly_normalize(&r, mod);
    return r;
}

/* Ділення многочленів з остачею: a = q * b + rem */
static void poly_div_rem(const Poly *a, const Poly *b, Poly *q, Poly *rem, int mod) {
    *rem = *a;
    *q = poly_zero();
    if (b->deg == 0 && b->c[0] == 0) return; /* Помилка ділення на нуль */
    if (a->deg < b->deg) return;

    q->deg = a->deg - b->deg;
    int b_lead_inv = mod_inv(b->c[b->deg], mod);

    while (rem->deg >= b->deg && !(rem->deg == 0 && rem->c[0] == 0)) {
        int shift = rem->deg - b->deg;
        int factor = (rem->c[rem->deg] * b_lead_inv) % mod;
        q->c[shift] = factor;

        for (int i = 0; i <= b->deg; i++) {
            int sub_val = (factor * b->c[i]) % mod;
            rem->c[i + shift] = (rem->c[i + shift] - sub_val + mod) % mod;
        }
        poly_normalize(rem, mod);
    }
    poly_normalize(q, mod);
}

/* Найбільший спільний дільник многочленів (Алгоритм Евкліда) */
static Poly poly_gcd(const Poly *a, const Poly *b, int mod) {
    Poly x = *a, y = *b;
    while (!(y.deg == 0 && y.c[0] == 0)) {
        Poly q, rem;
        poly_div_rem(&x, &y, &q, &rem, mod);
        x = y;
        y = rem;
    }
    /* Нормування: старший коефіцієнт робимо 1 */
    if (x.c[x.deg] != 0) {
        int inv = mod_inv(x.c[x.deg], mod);
        for (int i = 0; i <= x.deg; i++) {
            x.c[i] = (x.c[i] * inv) % mod;
        }
    }
    return x;
}

/* Модульне піднесення: (base^exp) mod m */
static Poly poly_pow_mod(Poly base, int exp, const Poly *m, int mod) {
    Poly res = poly_zero();
    res.c[0] = 1; /* Одиничний многочлен */
    Poly q, rem;

    poly_div_rem(&base, m, &q, &base, mod);
    while (exp > 0) {
        if (exp & 1) {
            Poly prod = poly_mul(&res, &base, mod);
            poly_div_rem(&prod, m, &q, &res, mod);
        }
        Poly base_sq = poly_mul(&base, &base, mod);
        poly_div_rem(&base_sq, m, &q, &base, mod);
        exp >>= 1;
    }
    return res;
}

/* Друк многочлена */
static void poly_print(const Poly *p) {
    bool first = true;
    for (int i = p->deg; i >= 0; i--) {
        if (p->c[i] == 0 && p->deg > 0) continue;
        if (!first && p->c[i] > 0) printf(" + ");
        if (i == 0) printf("%d", p->c[i]);
        else if (i == 1) {
            if (p->c[i] == 1) printf("x");
            else printf("%d*x", p->c[i]);
        } else {
            if (p->c[i] == 1) printf("x^%d", i);
            else printf("%d*x^%d", p->c[i], i);
        }
        first = false;
    }
    printf("\n");
}

/* Перевірка многочлена на незвідність за алгоритмом Рабіна */
static bool poly_is_irreducible(const Poly *f, int p) {
    if (f->deg <= 1) return (f->deg == 1);

    /* Формуємо x */
    Poly x_poly = poly_zero();
    x_poly.deg = 1;
    x_poly.c[1] = 1;

    /* Обчислюємо x^(p^n) mod f(x) послідовними піднесеннями */
    Poly h = x_poly;
    for (int i = 0; i < f->deg; i++) {
        h = poly_pow_mod(h, p, f, p);
    }
    Poly diff = poly_sub(&h, &x_poly, p);
    if (!(diff.deg == 0 && diff.c[0] == 0)) {
        return false; /* f(x) не ділить x^(p^n) - x */
    }

    /* Перевірка НСД для дільників n */
    int n = f->deg;
    for (int d = 1; d <= n / 2; d++) {
        if (n % d == 0) {
            Poly hd = x_poly;
            for (int i = 0; i < d; i++) {
                hd = poly_pow_mod(hd, p, f, p);
            }
            Poly diff_d = poly_sub(&hd, &x_poly, p);
            Poly g = poly_gcd(&diff_d, f, p);
            if (g.deg > 0) {
                return false; /* Знайдено спільний дільник меншого степеня */
            }
        }
    }
    return true;
}

int main(void) {
    printf("=== Факторизація та перевірка незвідності над F_2 ===\n\n");

    /* Тестовий многочлен: AES irreducible poly x^8 + x^4 + x^3 + x + 1 */
    Poly aes_poly = poly_zero();
    aes_poly.deg = 8;
    aes_poly.c[8] = 1; aes_poly.c[4] = 1; aes_poly.c[3] = 1; aes_poly.c[1] = 1; aes_poly.c[0] = 1;

    printf("Многочлен 1: ");
    poly_print(&aes_poly);
    printf("Статус незвідності: %s\n\n", poly_is_irreducible(&aes_poly, 2) ? "НЕПРИВІДНИЙ" : "ЗВІДНИЙ");

    /* Складений многочлен: (x^3 + x + 1) * (x^4 + x + 1) над F_2 */
    Poly p1 = poly_zero(); p1.deg = 3; p1.c[3] = 1; p1.c[1] = 1; p1.c[0] = 1;
    Poly p2 = poly_zero(); p2.deg = 4; p2.c[4] = 1; p2.c[1] = 1; p2.c[0] = 1;
    Poly composite = poly_mul(&p1, &p2, 2);

    printf("Многочлен 2 (добуток): ");
    poly_print(&composite);
    printf("Статус незвідності: %s\n", poly_is_irreducible(&composite, 2) ? "НЕПРИВІДНИЙ" : "ЗВІДНИЙ");

    /* Distinct-Degree факторизація для composite */
    printf("Пошук незвідних множників (Distinct-Degree):\n");
    Poly current = composite;
    Poly x_poly = poly_zero(); x_poly.deg = 1; x_poly.c[1] = 1;
    Poly h = x_poly;

    for (int d = 1; d <= current.deg / 2; d++) {
        h = poly_pow_mod(h, 2, &current, 2);
        Poly diff = poly_sub(&h, &x_poly, 2);
        Poly factor = poly_gcd(&diff, &current, 2);
        if (factor.deg > 0) {
            printf("  Знайдено множник степеня %d: ", d);
            poly_print(&factor);
            Poly q, rem;
            poly_div_rem(&current, &factor, &q, &rem, 2);
            current = q;
        }
    }
    if (current.deg > 0) {
        printf("  Залишковий незвідний множник степеня %d: ", current.deg);
        poly_print(&current);
    }

    return 0;
}
