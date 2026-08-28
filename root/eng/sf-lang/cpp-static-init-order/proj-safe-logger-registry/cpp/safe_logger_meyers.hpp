// safe_logger_meyers.hpp
#pragma once
#include <string>
#include <iostream>

class SafeLogger {
public:
    explicit SafeLogger(const std::string& prefix) : m_prefix(prefix) {
        std::cout << "[MEYERS INIT] Журнал " << m_prefix << " активовано\n";
    }

    void log(const std::string& msg) const {
        std::cout << "[" << m_prefix << "] " << msg << "\n";
    }

    // Фабричний метод доступу з гарантованою лінивою ініціалізацією
    static SafeLogger& instance() {
        // Потокобезпечно за стандартом C++11 (Magic Statics)
        static SafeLogger s_instance("SAFE_MEYERS_LOG");
        return s_instance;
    }

private:
    std::string m_prefix;
};
