// safe_logger.hpp
#pragma once
#include <string>
#include <iostream>

class Logger {
public:
    explicit Logger(const std::string& log_file) 
        : m_filename(log_file), m_is_open(true) {
        std::cout << "[Logger] Файл відкрито: " << m_filename << "\n";
    }

    void log(const std::string& message) const {
        std::cout << "[" << m_filename << "] " << message << "\n";
    }

    // Статичний метод-фабрика доступу
    static Logger& instance() {
        // Локальна статична змінна: ініціалізується під час першого входу у функцію
        static Logger s_instance("application.log");
        return s_instance;
    }

private:
    std::string m_filename;
    bool m_is_open{false};
};
