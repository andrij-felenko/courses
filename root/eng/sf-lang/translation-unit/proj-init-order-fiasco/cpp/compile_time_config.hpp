// compile_time_config.hpp (C++20)
#pragma once
#include <string_view>

struct FastConfig {
    std::string_view prefix;
    int max_retries;

    // constexpr-конструктор дозволяє обчислення під час компіляції
    constexpr FastConfig(std::string_view p, int r) noexcept
        : prefix(p), max_retries(r) {}
};

// constinit гарантує відсутність будь-якого динамічного коду запуску.
// Якщо вираз не може бути обчислений під час компіляції, збірка завершиться з помилкою.
constinit inline FastConfig g_fast_config{"[APP_CONSTINIT]", 5};
