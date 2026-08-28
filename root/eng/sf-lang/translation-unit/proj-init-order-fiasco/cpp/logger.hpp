// logger.hpp
#pragma once
#include "config.hpp"
#include <iostream>
#include <string_view>

class Logger {
public:
    Logger() {
        // Небезпека: g_config у сусідньому TU може бути ще не сконструйованим!
        // Читання поля std::string призведе до звернення до нульового покажчика.
        std::cout << g_config.prefix() << " Logger subsystem online.\n";
    }

    void log(std::string_view message) const {
        std::cout << g_config.prefix() << " " << message << "\n";
    }
};

extern Logger g_logger;
