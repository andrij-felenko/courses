#include <iostream>
#include <string_view>
#include <array>
#include <span>
#include <expected>
#include <algorithm>

constexpr size_t UsernameMaxCapacity = 64;

enum class CopyError {
    BufferOverflow,
    InvalidInput
};

// Ідіоматична функція C++23 з використанням std::span та std::expected
template <size_t N>
std::expected<void, CopyError> copy_username_safe(
    std::array<char, N>& destination, 
    std::string_view source
) noexcept {
    if (source.empty()) {
        return std::unexpected(CopyError::InvalidInput);
    }

    // std::string_view зберігає розмір, унеможливлюючи сканування довільної пам'яті
    if (source.size() >= N) {
        return std::unexpected(CopyError::BufferOverflow);
    }

    std::copy(source.begin(), source.end(), destination.begin());
    destination[source.size()] = '\0';
    return {};
}
