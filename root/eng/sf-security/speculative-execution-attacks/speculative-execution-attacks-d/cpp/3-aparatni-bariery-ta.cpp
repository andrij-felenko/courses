#include <cstdint>
#include <cstddef>
#include <optional>
#include <span>
#include <x86intrin.h>

[[nodiscard]] std::optional<uint8_t> secure_read(std::span<const uint8_t> arr, size_t index) noexcept {
    if (index < arr.size()) {
        // Бар'єр запобігає випереджальному доступу до пам'яті
        _mm_lfence();
        return arr[index];
    }
    return std::nullopt;
}
