// logger_safe.hpp
#pragma once
#include "config_safe.hpp"
#include <iostream>
#include <string_view>

class Logger {
public:
    Logger() {
        // Гарантовано безпечно: перший виклик get_config() змусить рантайм
        // сконструювати instance перед тим, як повернути посилання.
        std::cout << get_config().prefix() << " Logger online safely.\n";
    }

    void log(std::string_view message) const {
        std::cout << get_config().prefix() << " " << message << "\n";
    }
};

inline Logger& get_logger() {
    static Logger instance;
    return instance;
}
