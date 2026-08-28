std::vector<int> data = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

// Створення конвеєра адаптерів над std::span без виділення пам'яті
auto even_squares = std::span{data}
                  | std::views::filter([](int n) { return n % 2 == 0; })
                  | std::views::transform([](int n) { return n * n; });

for (int val : even_squares) {
    // Обробка обчислених значень
}
