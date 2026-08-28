#include <cstdint>
#include <utility>
#include <concepts>
#include <expected>
#include <limits>

template <std::signed_integral T>
struct DivResult {
    T quot;
    T rem;
};

enum class DivError {
    DivisionByZero,
    Overflow
};

// Ідіоматичний C++23 результат ділення через std::expected
template <std::signed_integral T>
[[nodiscard]] constexpr std::expected<DivResult<T>, DivError> floor_div(T a, T b) noexcept {
    if (b == 0) {
        return std::unexpected(DivError::DivisionByZero);
    }
    if (a == std::numeric_limits<T>::min() && b == -1) {
        return std::unexpected(DivError::Overflow);
    }
    
    T q = a / b;
    T r = a % b;
    
    if (r != 0 && ((a < 0) ^ (b < 0))) {
        q -= 1;
        r += b;
    }
    return DivResult<T>{q, r};
}

template <std::signed_integral T>
[[nodiscard]] constexpr std::expected<DivResult<T>, DivError> euclidean_div(T a, T b) noexcept {
    if (b == 0) {
        return std::unexpected(DivError::DivisionByZero);
    }
    if (a == std::numeric_limits<T>::min() && b == -1) {
        return std::unexpected(DivError::Overflow);
    }
    
    T q = a / b;
    T r = a % b;
    
    if (r < 0) {
        if (b > 0) {
            q -= 1;
            r -= b;
        } else {
            q += 1;
            r -= b;
        }
    }
    return DivResult<T>{q, r};
}
