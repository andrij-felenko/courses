#include <cstdint>
#include <cstddef>
#include <span>

/**
 * @brief Безпечне порівняння двох буферів за константний час (C++20).
 * @return true, якщо вміст буферів повністю збігається.
 */
[[nodiscard]] bool crypto_verify_ct(std::span<const std::uint8_t> a, 
                                    std::span<const std::uint8_t> b) noexcept {
    if (a.size() != b.size()) {
        return false;
    }
    
    volatile std::uint_fast8_t diff = 0;
    for (std::size_t i = 0; i < a.size(); ++i) {
        diff |= static_cast<std::uint_fast8_t>(a[i] ^ b[i]);
    }
    
    return diff == 0;
}
