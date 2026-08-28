int main(void) {
    printf("=== Демонстрація арифметики ℤ[i] (C99) ===\n\n");

    /* 1. Алгоритм Евкліда */
    gauss_t a = gauss_make(11, 3);
    gauss_t b = gauss_make(1, 8);
    gauss_t g = gauss_canonical(gauss_gcd(a, b));
    printf("1. НСД для чисел (11 + 3i) та (1 + 8i):\n");
    printf("   gcd = %" PRId64 " + %" PRId64 "i, норма = %" PRIu64 "\n\n",
           g.re, g.im, gauss_norm(g));

    /* 2. Алгоритм Корначчі для розкладу p = a^2 + b^2 */
    uint64_t p = 2029;
    int64_t sq_a, sq_b;
    printf("2. Пошук розкладу p = %" PRIu64 " на суму квадратів:\n", p);
    if (solve_sum_of_two_squares(p, &sq_a, &sq_b)) {
        printf("   %" PRIu64 " = %" PRId64 "^2 + %" PRId64 "^2 = %" PRId64 " + %" PRId64 "\n\n",
               p, sq_a, sq_b, sq_a * sq_a, sq_b * sq_b);
    } else {
        printf("   Розклад неможливий (p != 1 mod 4)\n\n");
    }

    /* 3. Повна факторизація гауссового числа */
    gauss_t num = gauss_make(30, 10);
    gauss_factorization_t fact = gauss_factorize(num);
    printf("3. Факторизація числа (30 + 10i), норма = %" PRIu64 ":\n",
           gauss_norm(num));
    printf("   Одиниця розкладу: %" PRId64 " + %" PRId64 "i\n",
           fact.unit.re, fact.unit.im);
    for (int i = 0; i < fact.count; ++i) {
        printf("   Множник %d: (%" PRId64 " + %" PRId64 "i)^%d (норма = %" PRIu64 ")\n",
               i + 1,
               fact.factors[i].prime.re,
               fact.factors[i].prime.im,
               fact.factors[i].power,
               gauss_norm(fact.factors[i].prime));
    }

    return 0;
}
