#ifndef GALOIS_TYPES_HPP
#define GALOIS_TYPES_HPP

#include <array>
#include <cstdint>
#include <cstddef>
#include <system_error>

namespace galois {

/**
 * @brief C++20 коди помилок у вигляді скінченного перелічення
 */
enum class ErrorCode : int {
    Success = 0,
    NullPointer = -1,
    DivisionByZero = -2,
    InvalidPolynomial = -3,
    OutOfBounds = -4,
    NotInitialized = -5
};

/**
 * @brief Метадані та атрибути поля GF(2^m)
 */
template <typename T>
struct FieldContext {
    uint64_t poly{0};
    uint64_t field_size{0};
    uint64_t poly_mask{0};
    uint8_t m{0};
    bool is_primitive{false};
};

/**
 * @brief Таблиці експонент та дискретних логарифмів
 */
template <size_t Order = 256>
struct FieldTables {
    std::array<uint8_t, Order * 2> exp_table{};
    std::array<uint8_t, Order> log_table{};
    bool initialized{false};
};

} // namespace galois

#endif // GALOIS_TYPES_HPP
