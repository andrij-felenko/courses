// math_engine.ixx (або math_engine.cppm)
export module math_engine; // Оголошення модуля

// Ця функція експортується та доступна тим, хто робить import:
export int calculate_factorial(int n) noexcept {
    int res = 1;
    for (int i = 2; i <= n; ++i) res *= i;
    return res;
}

// Ця функція має module linkage: вона видима всередині модуля math_engine,
// але недоступна ззовні, навіть якщо знаходиться в іншій частині цього ж модуля!
int internal_helper(int x) noexcept {
    return x * 2;
}
