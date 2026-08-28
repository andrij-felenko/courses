#include <iostream>
#include <vector>
#include <cstddef>
#include <optional>

// Шаблонний лінійний пошук із вартовим у C++
template <typename T>
std::optional<std::size_t> search_with_sentinel(std::vector<T>& vec, const T& target) {
    if (vec.empty()) {
        return std::nullopt;
    }

    const std::size_t n = vec.size();
    vec.push_back(target); // Додаємо вартового в кінець буфера

    std::size_t i = 0;
    while (vec[i] != target) {
        ++i;
    }

    vec.pop_back(); // Прибираємо вартового

    if (i < n) {
        return i;
    }
    return std::nullopt;
}
