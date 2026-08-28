int main(void) {
    printf("=== Демонстрація розв'язання рівняння Пелля ===\n");
    uint64_t d = 61;
    PellSolution fund = pell_solve_fundamental(d);
    if (fund.found) {
        printf("Фундаментальний розв'язок для D = %llu:\n  x₁ = ", (unsigned long long)d);
        print_u128(fund.x);
        printf("\n  y₁ = ");
        print_u128(fund.y);
        printf("\n");

        PellSolution sol2 = pell_next_solution(fund, fund, d);
        printf("Другий розв'язок (x₂, y₂):\n  x₂ = ");
        print_u128(sol2.x);
        printf("\n  y₂ = ");
        print_u128(sol2.y);
        printf("\n");
    }

    printf("\n=== Довблення гіперкуба (Пошук піфагорової трійки) ===\n");
    // Многочлен P(x, y, z) = (x^2 + y^2 - z^2)^2 + (x - 3)^2 [для фіксації x=3, y>0]
    int64_t pythagoras_test(const int64_t* v, size_t n) {
        (void)n;
        int64_t x = v[0], y = v[1], z = v[2];
        if (x == 0 || y == 0 || z == 0) return -1;
        return (x * x + y * y - z * z) * (x * x + y * y - z * z) + (x - 3) * (x - 3);
    }

    // Модульне сито перед перебором
    if (!modular_sieve_check(pythagoras_test, 3, 4)) {
        printf("Рівняння відхилено модульним ситом за модулем 4.\n");
    } else {
        printf("Модульне сито пройдено успішно. Запуск довблення...\n");
        int64_t sol[3] = {0};
        SearchStats stats;
        if (diophantine_dovetail_search(pythagoras_test, 3, 10, sol, &stats)) {
            printf("Знайдено розв'язок: x=%lld, y=%lld, z=%lld (Оцінено точок: %llu)\n",
                   (long long)sol[0], (long long)sol[1], (long long)sol[2], 
                   (unsigned long long)stats.evaluated_points);
        }
    }

    return 0;
}
