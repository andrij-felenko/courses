// constinit_logger.hpp
#pragma once
#include <string_view>
#include <iostream>

class ConstinitLogger {
public:
    constexpr explicit ConstinitLogger(std::string_view tag) : m_tag(tag) {}

    void log(std::string_view msg) const {
        std::cout << "[" << m_tag << "] " << msg << "\n";
    }

private:
    std::string_view m_tag;
};

// Гарантовано заповнюється нульовою/константною фазою до старту .init_array
inline constinit ConstinitLogger g_constinit_log("SYSTEM_CONSTINIT");
