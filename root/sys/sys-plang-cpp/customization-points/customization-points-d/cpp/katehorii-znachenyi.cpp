#include <vector>
#include <ranges>

std::vector<int> get_vector() {
    return {1, 2, 3, 4, 5};
}

void process_dangling_example() {
    // ❌ ПОМИЛКА КОМПІЛЯЦІЇ у C++20:
    // std::ranges::begin(get_vector()) заборонено, оскільки get_vector() повертає rvalue,
    // і повернений ітератор став би висячим одразу після завершення виразу!
    
    // auto it = std::ranges::begin(get_vector()); // Не скомпільовано завдяки концепту borrowed_range

    // ✅ ПРАВИЛЬНО: зберегти об'єкт у lvalue змінну
    auto vec = get_vector();
    auto it = std::ranges::begin(vec);
}
