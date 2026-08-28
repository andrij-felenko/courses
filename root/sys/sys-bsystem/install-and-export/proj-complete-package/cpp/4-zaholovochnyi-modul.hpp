#pragma once

#include <concepts>
#include <span>
#include <numeric>

namespace hyperion::math {

template <typename T>
requires std::floating_point<T> || std::integral<T>
[[nodiscard]] constexpr T accumulate_span(std::span<const T> values) noexcept {
    return std::accumulate(values.begin(), values.end(), T{0});
}

} // namespace hyperion::math
