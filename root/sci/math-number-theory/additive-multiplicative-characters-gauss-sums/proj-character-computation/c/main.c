#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Швидке піднесення до степеня за модулем: (base^exp) % mod
static long long power_mod(long long base, long long exp, long long mod) {
    long long res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp % 2 == 1) res = (res * base) % mod;
        base = (base * base) % mod;
        exp /= 2;
    }
    return res;
}

// Пошук найменшого первісного кореня mod p
static int find_primitive_root(int p) {
    if (p == 2) return 1;
    int phi = p - 1;
    int n = phi;
    int prime_factors[32];
    int num_factors = 0;

    // Факторизація числа phi = p - 1
    for (int i = 2; i * i <= n; i++) {
        if (n % i == 0) {
            prime_factors[num_factors++] = i;
            while (n % i == 0) n /= i;
        }
    }
    if (n > 1) prime_factors[num_factors++] = n;

    // Перевірка кандидатів на первісний корінь
    for (int g = 2; g < p; g++) {
        bool ok = true;
        for (int i = 0; i < num_factors; i++) {
            if (power_mod(g, phi / prime_factors[i], p) == 1) {
                ok = false;
                break;
            }
        }
        if (ok) return g;
    }
    return -1;
}

// Структура контексту характерів Діріхле
typedef struct {
    int p;
    int g;
    int *dlog; // dlog[x] = k таке, що g^k = x mod p
} CharacterContext;

// Ініціалізація та виділення пам'яті під контекст
CharacterContext* char_ctx_create(int p) {
    CharacterContext *ctx = (CharacterContext*)malloc(sizeof(CharacterContext));
    if (!ctx) return NULL;
    ctx->p = p;
    ctx->g = find_primitive_root(p);
    ctx->dlog = (int*)calloc(p, sizeof(int));
    if (!ctx->dlog) {
        free(ctx);
        return NULL;
    }

    // Побудова таблиці дискретного логарифмування за O(p)
    long long val = 1;
    for (int k = 0; k < p - 1; k++) {
        ctx->dlog[val] = k;
        val = (val * ctx->g) % p;
    }
    return ctx;
}

// Звільнення динамічної пам'яті
void char_ctx_free(CharacterContext *ctx) {
    if (ctx) {
        free(ctx->dlog);
        free(ctx);
    }
}

// Обчислення значення характера χ_m(n)
double complex eval_character(const CharacterContext *ctx, int m, int n) {
    if (n % ctx->p == 0) return 0.0 + 0.0 * I;
    int k = ctx->dlog[n % ctx->p];
    double angle = 2.0 * M_PI * m * k / (ctx->p - 1);
    return cos(angle) + sin(angle) * I;
}

// Обчислення суми Ґаусса g(χ_m)
double complex compute_gauss_sum(const CharacterContext *ctx, int m) {
    double complex sum = 0.0 + 0.0 * I;
    int p = ctx->p;
    for (int x = 1; x < p; x++) {
        double complex chi_val = eval_character(ctx, m, x);
        double add_angle = 2.0 * M_PI * x / p;
        double complex add_val = cos(add_angle) + sin(add_angle) * I;
        sum += chi_val * add_val;
    }
    return sum;
}

// Перевірка ортогональності характерів
bool check_orthogonality(const CharacterContext *ctx) {
    int phi = ctx->p - 1;
    double eps = 1e-7;
    for (int i = 0; i < phi; i++) {
        for (int j = 0; j < phi; j++) {
            double complex sum = 0.0 + 0.0 * I;
            for (int x = 1; x < ctx->p; x++) {
                double complex c1 = eval_character(ctx, i, x);
                double complex c2 = eval_character(ctx, j, x);
                sum += c1 * conj(c2);
            }
            double expected = (i == j) ? (double)phi : 0.0;
            if (cabs(sum - expected) > eps) return false;
        }
    }
    return true;
}

int main(void) {
    int p = 7;
    CharacterContext *ctx = char_ctx_create(p);
    if (!ctx) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    printf("=== Модуль p = %d, Первісний корінь g = %d ===\n", ctx->p, ctx->g);

    printf("\nТаблиця характерів χ_m(x):\n");
    printf("m\\x ");
    for (int x = 1; x < p; x++) printf("   x=%d  ", x);
    printf("\n");

    for (int m = 0; m < p - 1; m++) {
        printf("χ_%d ", m);
        for (int x = 1; x < p; x++) {
            double complex val = eval_character(ctx, m, x);
            printf("%+.1f%+.1fi ", creal(val), cimag(val));
        }
        printf("\n");
    }

    printf("\nСуми Ґаусса та перевірка |g(χ)| = √%d:\n", p);
    for (int m = 0; m < p - 1; m++) {
        double complex g_sum = compute_gauss_sum(ctx, m);
        double mod = cabs(g_sum);
        printf("g(χ_%d) = %+.3f %+.3fi | |g| = %.4f (теоретично: %.4f)\n",
               m, creal(g_sum), cimag(g_sum), mod, sqrt((double)p));
    }

    bool orth_ok = check_orthogonality(ctx);
    printf("\nОртогональність матриці характерів: %s\n", orth_ok ? "ПРОЙДЕНО" : "ПОМИЛКА");

    char_ctx_free(ctx);
    return 0;
}
