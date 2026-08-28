#include <iostream>

// Перевірка підтримки узагальнених лямбд стандарту C++14
#if defined(__cpp_generic_lambdas) && __cpp_generic_lambdas >= 201304L
    #define HAS_GENERIC_LAMBDAS 1
#else
    #define HAS_GENERIC_LAMBDAS 0
#endif

// Перевірка наявності розширеного constexpr C++14
#if defined(__cpp_constexpr) && __cpp_constexpr >= 201304L
    #define HAS_RELAXED_CONSTEXPR 1
#else
    #define HAS_RELAXED_CONSTEXPR 0
#endif

// Перевірка двійкових літералів
#if defined(__cpp_binary_literals) && __cpp_binary_literals >= 201304L
    constexpr auto bitmask = 0b1010'1111;
#else
    constexpr auto bitmask = 0xAF;
#endif
