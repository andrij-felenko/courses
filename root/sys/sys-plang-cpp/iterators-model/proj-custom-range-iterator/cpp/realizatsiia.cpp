#include <iostream>
#include <concepts>
#include <iterator>
#include <algorithm>

// Об'єкт-вартовий C++20 для нуль-термінованих рядків
struct NullTerminatedSentinel {
    // Порівняння вартового з будь-яким ітератором, що читає char
    template<std::indirectly_readable It>
    requires std::same_as<std::iter_value_t<It>, char>
    friend constexpr bool operator==(It it, NullTerminatedSentinel) {
        return *it == '\0'; // Умова зупинки — досягнення нуля
    }
};

int main() {
    const char* text = "Hello, C++20 Sentinels!";

    // Обхід діапазону [text, NullTerminatedSentinel{})
    std::cout << "C++20 Sentinel traversal: ";
    for (auto it = text; it != NullTerminatedSentinel{}; ++it) {
        std::cout << *it;
    }
    std::cout << "\n";

    // Перевірка відповідності концепту std::sentinel_for під час компіляції
    static_assert(std::sentinel_for<NullTerminatedSentinel, const char*>);

    // Використання зі стандартними алгоритмами C++20 ranges
    auto count = std::ranges::distance(text, NullTerminatedSentinel{});
    std::cout << "Computed string length via sentinel without strlen(): " << count << "\n";

    return 0;
}
