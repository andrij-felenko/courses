#include <cstddef>
#include <span>

// Еквівалентний C++ цикл із раннім перериванням
[[nodiscard]] int naive_compare(std::span<const std::byte> s1, 
                                std::span<const std::byte> s2) noexcept {
    const std::size_t n = s1.size() < s2.size() ? s1.size() : s2.size();
    for (std::size_t i = 0; i < n; ++i) {
        if (s1[i] != s2[i]) {
            return static_cast<int>(s1[i]) - static_cast<int>(s2[i]);
        }
    }
    return 0;
}
