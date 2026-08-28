// compat/attributes.hpp
#pragma once

// Портативний атрибут оптимізації порожніх членів
#if defined(_MSC_VER) && !defined(__clang__)
    // Для компілятора MSVC використовуємо вендорний атрибут
    #define COMPAT_NO_UNIQUE_ADDRESS [[msvc::no_unique_address]]
#elif defined(__has_cpp_attribute)
    #if __has_cpp_attribute(no_unique_address) >= 201803L
        #define COMPAT_NO_UNIQUE_ADDRESS [[no_unique_address]]
    #else
        #define COMPAT_NO_UNIQUE_ADDRESS
    #endif
#else
    #define COMPAT_NO_UNIQUE_ADDRESS
#endif

// Портативний атрибут [[nodiscard]] з підтримкою текстового пояснення (C++20)
#if defined(__has_cpp_attribute)
    #if __has_cpp_attribute(nodiscard) >= 201907L
        #define COMPAT_NODISCARD_MSG(msg) [[nodiscard(msg)]]
        #define COMPAT_NODISCARD [[nodiscard]]
    #elif __has_cpp_attribute(nodiscard) >= 201603L
        #define COMPAT_NODISCARD_MSG(msg) [[nodiscard]]
        #define COMPAT_NODISCARD [[nodiscard]]
    #else
        #define COMPAT_NODISCARD_MSG(msg)
        #define COMPAT_NODISCARD
    #endif
#else
    #define COMPAT_NODISCARD_MSG(msg)
    #define COMPAT_NODISCARD
#endif
