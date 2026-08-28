#pragma once

#include "compat/config.hpp"
#include "compat/span.hpp"
#include <numeric>
#include <type_traits>

namespace compat {

#if COMPAT_HAS_CONCEPTS

    // Сучасна гілка C++20: декларативні концепції та обмеження requires
    template <typename T>
    concept Numeric = std::is_arithmetic_v<T>;

    template <Numeric T>
    COMPAT_NODISCARD("Ігнорування результату обчислення суми")
    constexpr T fast_accumulate(compat::span<const T> data) noexcept {
        T sum = 0;
        for (const auto& elem : data) {
            sum += elem;
        }
        return sum;
    }

#else

    // Сумісна гілка C++14: SFINAE-перевантаження через трейти типів
    template <typename T, typename = std::enable_if_t<std::is_arithmetic<T>::value>>
    COMPAT_NODISCARD("Ігнорування результату обчислення суми")
    constexpr T fast_accumulate(compat::span<const T> data) noexcept {
        T sum = 0;
        for (std::size_t i = 0; i < data.size(); ++i) {
            sum += data[i];
        }
        return sum;
    }

#endif

}
