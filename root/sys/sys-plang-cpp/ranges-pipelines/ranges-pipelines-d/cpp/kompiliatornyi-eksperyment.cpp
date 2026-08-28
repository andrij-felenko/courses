// Код 1: Конвеєр Ranges
int sum_even_squares(const std::vector<int>& v) {
    int sum = 0;
    for (int x : v | std::views::filter([](int n){ return n % 2 == 0; })
                  | std::views::transform([](int n){ return n * n; })) {
        sum += x;
    }
    return sum;
}

// Код 2: Ручний цикл
int sum_even_squares_manual(const std::vector<int>& v) {
    int sum = 0;
    for (size_t i = 0; i < v.size(); ++i) {
        if (v[i] % 2 == 0) {
            sum += v[i] * v[i];
        }
    }
    return sum;
}
