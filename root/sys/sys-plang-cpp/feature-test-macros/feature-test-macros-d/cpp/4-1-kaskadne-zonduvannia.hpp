#pragma once

// Крок 1: Безпечно підключаємо <version>, якщо він підтримується препроцесором
#if defined(__has_include)
    #if __has_include(<version>)
        #include <version>
    #endif
#endif

// Крок 2: Перевіряємо наявність макросу std::span потрібної версії
#if defined(__cpp_lib_span) && __cpp_lib_span >= 202002L
    #include <span>
    namespace mylib {
        using std::span;
        using std::dynamic_extent;
    }
#else
    #include "mylib/fallback/span.hpp"
    namespace mylib {
        using fallback::span;
        using fallback::dynamic_extent;
    }
#endif
