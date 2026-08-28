/* bit_ops.hpp — Ідіоматична бібліотека бітових операцій мовою C++20 */
#pragma once

#include <bit>
#include <concepts>
#include <cstdint>
#include <cstddef>
#include <optional>
#include <expected>
#include <string_view>

namespace bitops {

enum class BitError {
    OutOfRange,
    NotFound,
    InvalidArgument
};

/* Концепт для суворо беззнакових цілих типів */
template <typename T>
concept UnsignedWord = std::unsigned_integral<T>;

/* Обчислення ваги Гемінга (кількості одиниць) для довільного беззнакового типу */
template <UnsignedWord T>
[[nodiscard]] constexpr int popcount(T value) noexcept {
    return std::popcount(value);
}

/* Обчислення парності (true — непарна кількість одиниць, false — парна) */
template <UnsignedWord T>
[[nodiscard]] constexpr bool parity(T value) noexcept {
    return (std::popcount(value) & 1) != 0;
}

/* Обчислення рангу одиниць у слові на діапазоні розрядів [0..bit_idx] */
template <UnsignedWord T>
[[nodiscard]] constexpr std::expected<size_t, BitError> rank1(T word, size_t bit_idx) noexcept {
    constexpr size_t total_bits = sizeof(T) * 8;
    if (bit_idx >= total_bits) {
        return std::unexpected(BitError::OutOfRange);
    }
    const T mask = (bit_idx == total_bits - 1) 
        ? static_cast<T>(~static_cast<T>(0)) 
        : static_cast<T>((static_cast<T>(1) << (bit_idx + 1)) - static_cast<T>(1));
    return static_cast<size_t>(std::popcount(static_cast<T>(word & mask)));
}

/* Дуальний ранг нулів */
template <UnsignedWord T>
[[nodiscard]] constexpr std::expected<size_t, BitError> rank0(T word, size_t bit_idx) noexcept {
    auto r1 = rank1(word, bit_idx);
    if (!r1) return std::unexpected(r1.error());
    return (bit_idx + 1) - *r1;
}

/* Пошук позиції k-ї одиниці (1-індексація для k) */
template <UnsignedWord T>
[[nodiscard]] constexpr std::expected<size_t, BitError> select1(T word, size_t k) noexcept {
    constexpr size_t total_bits = sizeof(T) * 8;
    if (k == 0 || k > total_bits) {
        return std::unexpected(BitError::InvalidArgument);
    }
    if (static_cast<size_t>(std::popcount(word)) < k) {
        return std::unexpected(BitError::NotFound);
    }

    size_t low = 0;
    size_t high = total_bits - 1;
    size_t result = total_bits - 1;

    while (low <= high) {
        size_t mid = low + (high - low) / 2;
        const T mask = (mid == total_bits - 1)
            ? static_cast<T>(~static_cast<T>(0))
            : static_cast<T>((static_cast<T>(1) << (mid + 1)) - static_cast<T>(1));

        if (static_cast<size_t>(std::popcount(static_cast<T>(word & mask))) >= k) {
            result = mid;
            if (mid == 0) break;
            high = mid - 1;
        } else {
            low = mid + 1;
        }
    }
    return result;
}

} // namespace bitops
