#include <cstdint>
#include <cstddef>
#include <span>
#include <optional>
#include <x86intrin.h>

namespace security {

template <typename T>
[[nodiscard]] size_t sanitize_index(size_t index, size_t limit) noexcept {
    const auto s_idx = static_cast<int64_t>(index);
    const auto s_lim = static_cast<int64_t>(limit);
    const int64_t mask = ((s_idx ^ s_lim) | (s_idx - s_lim)) >> 63;
    return index & static_cast<size_t>(~mask);
}

template <typename T>
[[nodiscard]] std::optional<T> secure_read_fenced(std::span<const T> data, size_t index) noexcept {
    if (index < data.size()) {
        _mm_lfence(); // Бар'єр серіалізації: гарантує завершення перевірки меж
        return data[index];
    }
    return std::nullopt;
}

} // namespace security
