#pragma once

// 1. Безпечне зондування та підключення нормативного заголовка <version>
#if defined(__has_include)
    #if __has_include(<version>)
        #include <version>
    #endif
#endif

// 2. Зондування підтримки мовних концепцій ядра (C++20)
#if defined(__cpp_concepts) && __cpp_concepts >= 201907L
    #define COMPAT_HAS_CONCEPTS 1
    #define COMPAT_REQUIRES(...) requires __VA_ARGS__
#else
    #define COMPAT_HAS_CONCEPTS 0
    #define COMPAT_REQUIRES(...)
#endif

// 3. Зондування функцій негайного обчислення consteval
#if defined(__cpp_consteval) && __cpp_consteval >= 201811L
    #define COMPAT_CONSTEVAL consteval
#else
    #define COMPAT_CONSTEVAL constexpr
#endif

// 4. Зондування розширеного constexpr (віртуальні методи, динамічна пам'ять)
#if defined(__cpp_constexpr) && __cpp_constexpr >= 201907L
    #define COMPAT_CONSTEXPR_20 constexpr
#else
    #define COMPAT_CONSTEXPR_20
#endif

// 5. Зондування синтаксичних атрибутів через оператор __has_cpp_attribute
#if defined(__has_cpp_attribute)
    #if __has_cpp_attribute(nodiscard) >= 201907L
        #define COMPAT_NODISCARD(msg) [[nodiscard(msg)]]
    #elif __has_cpp_attribute(nodiscard) >= 201603L
        #define COMPAT_NODISCARD(msg) [[nodiscard]]
    #else
        #define COMPAT_NODISCARD(msg)
    #endif

    #if __has_cpp_attribute(likely) >= 201803L
        #define COMPAT_LIKELY [[likely]]
        #define COMPAT_UNLIKELY [[unlikely]]
    #else
        #define COMPAT_LIKELY
        #define COMPAT_UNLIKELY
    #endif
#else
    #define COMPAT_NODISCARD(msg)
    #define COMPAT_LIKELY
    #define COMPAT_UNLIKELY
#endif
