// value_category_probe.hpp — вимірювач категорії виразу
#pragma once
#include <type_traits>

namespace probe {

struct lvalue_t  {};
struct xvalue_t  {};
struct prvalue_t {};

// Категорію закодовано ФОРМОЮ типу, який віддає decltype((expr))
template <typename T> struct category      { using tag = prvalue_t; };
template <typename T> struct category<T&>  { using tag = lvalue_t;  };
template <typename T> struct category<T&&> { using tag = xvalue_t;  };

// Псевдонім рятує від typename у шаблонному коді
template <typename T> using category_t = typename category<T>::tag;

constexpr const char* plain(lvalue_t)  { return "lvalue";  }
constexpr const char* plain(xvalue_t)  { return "xvalue";  }
constexpr const char* plain(prvalue_t) { return "prvalue"; }

constexpr const char* qualified(lvalue_t)  { return "const lvalue";  }
constexpr const char* qualified(xvalue_t)  { return "const xvalue";  }
constexpr const char* qualified(prvalue_t) { return "const prvalue"; }

template <typename T>
constexpr const char* describe() {
    if constexpr (std::is_const_v<std::remove_reference_t<T>>)
        return qualified(category_t<T>{});
    else
        return plain(category_t<T>{});
}

}  // namespace probe

// Для людини: рядок, який можна надрукувати
#define VALUE_CATEGORY(...) (::probe::describe<decltype((__VA_ARGS__))>())

// Для збірки: перевірка, яка ламає компіляцію при регресії
#define STATIC_CATEGORY(expected, ...)                                    \
    static_assert(                                                        \
        std::is_same_v<::probe::category_t<decltype((__VA_ARGS__))>,      \
                       ::probe::expected>,                                \
        "не та категорія виразу: " #__VA_ARGS__)
