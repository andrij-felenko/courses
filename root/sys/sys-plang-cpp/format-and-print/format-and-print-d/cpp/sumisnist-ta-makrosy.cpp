#include <version>

#if defined(__cpp_lib_print)
    #include <print>
    #define LOG_PRINT(...) std::print(__VA_ARGS__)
#elif defined(__cpp_lib_format)
    #include <format>
    #include <iostream>
    #define LOG_PRINT(...) std::cout << std::format(__VA_ARGS__)
#else
    // Фолбек для старіших компіляторів
    #include <fmt/core.h>
    #define LOG_PRINT(...) fmt::print(__VA_ARGS__)
#endif
