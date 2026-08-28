#include <iostream>
#include <string_view>
#include <array>
#include <span>
#include <expected>
#include <algorithm>

constexpr size_t MaxBufferSize = 64;

enum class BufferError {
    CapacityExceeded,
    EmptyBuffer
};

// Ідіоматичний підхід C++23 з використанням std::span та std::expected
template <size_t N>
std::expected<void, BufferError> safe_copy(std::array<char, N>& dest, std::string_view src) {
    if (src.empty()) {
        return std::unexpected(BufferError::EmptyBuffer);
    }
    
    if (src.size() >= N) {
        return std::unexpected(BufferError::CapacityExceeded);
    }
    
    std::copy(src.begin(), src.end(), dest.begin());
    dest[src.size()] = '\0';
    return {};
}

int main() {
    std::array<char, MaxBufferSize> destination{};
    std::string_view untrusted_input = "Untrusted input string payload";

    auto result = safe_copy(destination, untrusted_input);
    if (result.has_value()) {
        std::cout << "Успішно скопійовано: " << destination.data() << '\n';
    } else {
        std::cerr << "Помилка: вхідні дані перевищують розмір буфера!\n";
    }
    return 0;
}
