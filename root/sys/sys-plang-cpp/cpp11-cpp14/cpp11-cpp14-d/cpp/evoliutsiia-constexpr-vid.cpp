// C++11 стиль: жорстке обмеження одним return та рекурсією
constexpr int fact_c11(int n) {
    return (n <= 1) ? 1 : n * fact_c11(n - 1);
}

// C++14 стиль: нормальний цикл та локальна змінна
constexpr int fact_c14(int n) {
    int result = 1;
    for (int i = 2; i <= n; ++i) {
        result *= i;
    }
    return result;
}

// Перевірка значення на етапі компіляції (zero runtime cost)
static_assert(fact_c14(5) == 120, "Fact(5) must be 120");
