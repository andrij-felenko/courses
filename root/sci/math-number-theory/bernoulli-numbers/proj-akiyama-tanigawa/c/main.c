#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

// Структура точного раціонального числа
typedef struct {
    int64_t num; // Чисельник
    int64_t den; // Знаменник (завжди > 0)
} Rational;

// Найбільший спільний дільник (алгоритм Евкліда)
static int64_t gcd(int64_t a, int64_t b) {
    a = llabs(a);
    b = llabs(b);
    while (b != 0) {
        int64_t t = b;
        b = a % b;
        a = t;
    }
    return a;
}

// Скорочення дробу до канонічного вигляду
static Rational rat_reduce(int64_t num, int64_t den) {
    if (den == 0) {
        fprintf(stderr, "Помилка: ділення на нуль у раціональній арифметиці\n");
        exit(EXIT_FAILURE);
    }
    if (den < 0) {
        num = -num;
        den = -den;
    }
    int64_t g = gcd(num, den);
    Rational r = { num / g, den / g };
    return r;
}

// Віднімання двох раціональних чисел: r1 - r2
static Rational rat_sub(Rational r1, Rational r2) {
    int64_t g = gcd(r1.den, r2.den);
    int64_t den = (r1.den / g) * r2.den;
    int64_t num = r1.num * (r2.den / g) - r2.num * (r1.den / g);
    return rat_reduce(num, den);
}

// Множення раціонального числа на ціле: r * scalar
static Rational rat_mul_int(Rational r, int64_t scalar) {
    int64_t g = gcd(scalar, r.den);
    int64_t den = r.den / g;
    int64_t num = r.num * (scalar / g);
    return rat_reduce(num, den);
}

// Алгоритм Акіями — Таніґави для знаходження чисел Бернуллі
void compute_bernoulli_c(int n, Rational *b_out) {
    Rational *A = (Rational *)malloc((size_t)(n + 1) * sizeof(Rational));
    if (!A) {
        perror("Помилка виділення пам'яті");
        exit(EXIT_FAILURE);
    }

    // Ініціалізація: A[j] = 1 / (j + 1)
    for (int j = 0; j <= n; j++) {
        A[j] = rat_reduce(1, j + 1);
    }

    b_out[0] = A[0];

    // Ітеративне оновлення масиву A
    for (int i = 1; i <= n; i++) {
        for (int j = 0; j <= n - i; j++) {
            Rational diff = rat_sub(A[j], A[j + 1]);
            A[j] = rat_mul_int(diff, j + 1);
        }
        
        // Корекція знаку B1: Akiyama-Tanigawa дає B1 = +1/2,
        // а стандартна угода вимагає B1 = -1/2.
        if (i == 1) {
            b_out[1] = rat_reduce(-A[0].num, A[0].den);
        } else {
            b_out[i] = A[0];
        }
    }

    free(A);
}

int main(void) {
    const int max_n = 14;
    Rational B[15];

    compute_bernoulli_c(max_n, B);

    printf("=== Обчислення чисел Бернуллі B_0 .. B_%d (Мова C) ===\n\n", max_n);
    for (int i = 0; i <= max_n; i++) {
        printf("B_%-2d = %12lld / %-8lld", i, (long long)B[i].num, (long long)B[i].den);
        if (B[i].num != 0) {
            printf("  (≈ %+.10f)\n", (double)B[i].num / (double)B[i].den);
        } else {
            printf("  (  0.0000000000)\n");
        }
    }

    return 0;
}
