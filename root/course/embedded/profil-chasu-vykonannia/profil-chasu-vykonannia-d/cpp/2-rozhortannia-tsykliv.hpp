// Універсальний розгорнутий Dot Product на C++20 через std::index_sequence
#pragma once
#include <span>
#include <utility>
#include <concepts>

namespace embedded::math {

template <size_t N>
[[nodiscard]] inline float dot_product_unrolled(std::span<const float, N> a, 
                                                std::span<const float, N> b) noexcept {
    return [&]<size_t... Is>(std::index_sequence<Is...>) {
        return ((a[Is] * b[Is]) + ...); // C++17 Fold Expression розгортається у суму
    }(std::make_index_sequence<N>{});
}

} // namespace embedded::math
