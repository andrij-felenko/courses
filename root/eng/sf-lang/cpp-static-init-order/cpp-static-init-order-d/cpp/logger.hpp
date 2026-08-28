// logger.hpp
#pragma once
#include <string>
#include <iostream>

class Logger {
public:
    explicit Logger(const std::string& log_file) 
        : m_filename(log_file), m_is_open(true) {
        std::cout << "[Logger] Відкрито файл: " << m_filename << "\n";
    }

    void log(const std::string& message) const {
        if (!m_is_open) {
            std::cerr << "[Logger ERROR] Спроба запису в невідкритий журнал!\n";
            return;
        }
        std::cout << "[" << m_filename << "] " << message << "\n";
    }

private:
    std::string m_filename;
    bool m_is_open{false};
};

// Експорт глобального об'єкта журналу
extern Logger g_logger;
