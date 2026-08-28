// Створення власного адаптера шляхом композиції двох стандартних:
auto filter_even_and_square = std::views::filter([](int x) { return x % 2 == 0; })
                            | std::views::transform([](int x) { return x * x; });

// Застосування збереженого конвеєра до різних контейнерів:
std::vector<int> numbers = {1, 2, 3, 4, 5};
std::list<int> more_numbers = {10, 15, 20, 25};

auto res1 = numbers | filter_even_and_square;      // Результат: 4, 16
auto res2 = more_numbers | filter_even_and_square; // Результат: 100, 400
