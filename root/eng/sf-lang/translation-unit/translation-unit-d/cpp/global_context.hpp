// global_context.hpp (C++17)
#pragma once
#include <string>

struct AppConfig {
    std::string app_name = "CoreEngine";
    int worker_threads = 8;
};

// inline-змінна: дозволено визначення в заголовку,
// лінкер гарантує існування рівно одного екземпляра в пам'яті програми!
inline AppConfig g_app_config;
