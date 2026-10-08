#ifndef OLED_DISPLAY_HPP
#define OLED_DISPLAY_HPP

#include <cstdint>
#include <iostream>
#include <iomanip>
#include <string>
#include "water_flow_sensor.hpp"

class OledDisplay {
public:
    explicit OledDisplay(uint8_t i2c_addr = 0x3C) : i2c_address_(i2c_addr) {}

    void begin() {
        is_initialized_ = true;
        std::cout << "[OLED] Дисплей ініціалізовано (I2C: 0x" 
                  << std::hex << static_cast<int>(i2c_address_) << std::dec << ")\n";
    }

    // Відображення актуальних даних на дисплеї
    void render(const FlowMetrics& metrics, PowerState power_state, uint32_t current_time_ms) {
        if (!is_initialized_) return;

        // Оновлюємо екран не частіше ніж кожні 500 мс
        if (current_time_ms - last_render_ms_ < 500 && last_render_ms_ != 0) {
            return;
        }

        std::cout << "\n=====================================\n";
        std::cout << "         OLED DISPLAY (128x64)       \n";
        std::cout << "=====================================\n";
        std::cout << " Витрата : " << std::fixed << std::setprecision(2) 
                  << std::setw(6) << metrics.flow_rate_lpm << " л/хв\n";
        std::cout << " Заг.об'єм: " << std::fixed << std::setprecision(3) 
                  << std::setw(7) << metrics.total_liters << " л\n";
        std::cout << " Імпульси : " << std::setw(8) << metrics.total_pulses << "\n";
        std::cout << " Живлення : " << format_power_state(power_state) << "\n";
        std::cout << "=====================================\n";

        last_render_ms_ = current_time_ms;
    }

    void show_message(const std::string& message) {
        if (!is_initialized_) return;
        std::cout << "[OLED]: " << message << "\n";
    }

private:
    uint8_t i2c_address_;
    bool is_initialized_{false};
    uint32_t last_render_ms_{0};

    const char* format_power_state(PowerState state) const {
        switch (state) {
            case PowerState::Normal:   return "НОРМА";
            case PowerState::LowPower: return "ЕНЕРГОЗБЕРЕЖЕННЯ";
            case PowerState::Critical: return "КРИТИЧНЕ";
            default:                   return "НЕВІДОМО";
        }
    }
};

#endif // OLED_DISPLAY_HPP
