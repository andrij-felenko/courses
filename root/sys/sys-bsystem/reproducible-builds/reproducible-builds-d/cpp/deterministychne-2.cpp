// Детерміністичний підхід: використання канонічних констант версії
#include <iostream>
#include <string_view>

#ifndef PROJECT_VERSION_STRING
#define PROJECT_VERSION_STRING "1.0.0-release"
#endif

#ifndef MODULE_NAME
#define MODULE_NAME "core_engine"
#endif

void log_module_info() noexcept {
    // Детерміністично: версія фіксується системою контролю версій
    constexpr std::string_view version = PROJECT_VERSION_STRING;
    // Детерміністично: використовується логічне ім'я модуля замість шляху файлу
    constexpr std::string_view module = MODULE_NAME;
    std::cout << "Software Version: " << version << "\n";
    std::cout << "Module: " << module << "\n";
}
