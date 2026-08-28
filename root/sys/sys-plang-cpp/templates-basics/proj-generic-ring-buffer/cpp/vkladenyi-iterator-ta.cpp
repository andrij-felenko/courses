#include <ranges>

RingBuffer<int, 8> numbers;
numbers.push(10);
numbers.push(15);
numbers.push(20);
numbers.push(25);

// Повноцінна ітерація через Range-based for
for (const auto& val : numbers) {
    std::cout << val << " ";
}

// Конвеєрна обробка через C++20 Views
auto even_numbers = numbers 
                  | std::views::filter([](int n) { return n % 2 == 0; })
                  | std::views::transform([](int n) { return n * 2; });

for (int n : even_numbers) {
    std::cout << "Трансформоване парне: " << n << "\n";
}
