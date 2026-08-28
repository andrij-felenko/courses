#include <concepts>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>

template <std::equality_comparable T>
[[nodiscard]] std::optional<T> boyer_moore_majority(std::span<const T> data) noexcept {
    if (data.empty()) {
        return std::nullopt;
    }

    T candidate{};
    std::size_t count = 0;

    // Етап 1: Знаходження кандидата за один прохід
    for (const auto& item : data) {
        if (count == 0) {
            candidate = item;
            count = 1;
        } else if (item == candidate) {
            ++count;
        } else {
            --count;
        }
    }

    if (count == 0) {
        return std::nullopt;
    }

    // Етап 2: Верифікація реальної частоти кандидата
    std::size_t actual_frequency = 0;
    for (const auto& item : data) {
        if (item == candidate) {
            ++actual_frequency;
        }
    }

    if (actual_frequency > data.size() / 2) {
        return candidate;
    }

    return std::nullopt;
}
