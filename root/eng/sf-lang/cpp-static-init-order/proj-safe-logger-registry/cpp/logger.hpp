// logger.hpp
#pragma once
#include <string>
#include <iostream>

class Logger {
public:
    explicit Logger(const std::string& prefix) : m_prefix(prefix), m_ready(true) {
        std::cout << "[LOG INIT] Журнал " << m_prefix << " активовано\n";
    }

    void log(const std::string& msg) const {
        if (!m_ready) {
            std::cerr << "[FATAL] Спроба запису в неініціалізований журнал!\n";
        }
        std::cout << "[" << m_prefix << "] " << msg << "\n";
    }

private:
    std::string m_prefix;
    bool m_ready{false};
};

// Глобальне оголошення зовнішнього символу
extern Logger g_logger;
