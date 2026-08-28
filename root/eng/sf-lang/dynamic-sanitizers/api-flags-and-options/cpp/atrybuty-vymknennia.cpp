#include <cstddef>

// Вимкнення перевірок ASan у C++ за допомогою стандартного синтаксису атрибутів
[[gnu::no_sanitize("address")]]
void fast_memory_clear(std::byte* dest, std::size_t size) noexcept {
    for (std::size_t i = 0; i < size; ++i) {
        dest[i] = std::byte{0};
    }
}

// Вимкнення TSan для специфічного lock-free алгоритму
[[gnu::no_sanitize("thread")]]
auto read_relaxed_counter(const volatile unsigned int* counter) noexcept -> unsigned int {
    return *counter;
}
