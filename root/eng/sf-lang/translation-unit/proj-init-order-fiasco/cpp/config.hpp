// config.hpp
#pragma once
#include <string>

class Config {
public:
    Config() : log_prefix_("[APP_CORE]") {}
    
    [[nodiscard]] const std::string& prefix() const noexcept {
        return log_prefix_;
    }
private:
    std::string log_prefix_;
};

// Глобальний об'єкт із нетривіальним конструктором (External Linkage)
extern Config g_config;
