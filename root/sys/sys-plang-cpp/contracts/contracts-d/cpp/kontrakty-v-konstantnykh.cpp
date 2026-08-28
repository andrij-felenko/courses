constexpr int compute_factorial(int n) noexcept
    pre [non_negative]: n >= 0
    pre [no_overflow]: n <= 12
    post(r): r >= 1
{
    int result = 1;
    for (int i = 2; i <= n; ++i) {
        result *= i;
    }
    return result;
}

// Успішна компіляція: преумови виконані
constexpr int f5 = compute_factorial(5);

// Помилка компіляції: порушення преумови pre [no_overflow] для n = 15
// static_assert вимагає успішного завершення константного виразу
constexpr int f15 = compute_factorial(15);
