// config_safe.hpp
#pragma once
#include <string>

class Config {
public:
    Config() : log_prefix_("[APP_SAFE]") {}
    
    [[nodiscard]] const std::string& prefix() const noexcept {
        return log_prefix_;
    }
};

// Замість глобальної змінної — функція доступу
inline Config& get_config() {
    // Стандарт C++11 (Magic Statics): локальна статична змінна ініціалізується
    // строго при першому вході в функцію з повною потокобезпекою.
    static Config instance;
    return instance;
}
