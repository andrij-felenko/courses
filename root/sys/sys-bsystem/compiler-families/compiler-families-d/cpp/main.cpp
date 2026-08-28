#include <iostream>
#include <format>
#include <string_view>

// Стандартний C++20 підхід з використанням __VA_OPT__ та std::format
#define LOG_MSG_CPP(fmt_str, ...) \
    std::cout << std::format("[LOG] " fmt_str "\n" __VA_OPT__(,) __VA_ARGS__)

void run_cpp_demo() {
    LOG_MSG_CPP("System initialized");
    LOG_MSG_CPP("Values: {}, {}", 10, 20);
}
