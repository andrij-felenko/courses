constexpr int compute_factorial(int n)
    pre: n >= 0 && n <= 12
    post(r): r >= 1
{
    int res = 1;
    for (int i = 2; i <= n; ++i) {
        res *= i;
    }
    return res;
}

// Успішна компіляція: преумова n >= 0 виконується
constexpr int f5 = compute_factorial(5);

// Помилка компіляції: порушення преумови pre: n >= 0 && n <= 12
// static_assert вимагає коректного константного виразу
constexpr int f_bad = compute_factorial(-3); // Помилка: -3 не в діапазоні [0, 12]
