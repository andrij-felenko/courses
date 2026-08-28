// main.cpp — Ідіоматична взаємодія через RAII, std::filesystem та libgpiod C++
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <filesystem>
#include <chrono>
#include <gpiod.hpp>

namespace {
    constexpr std::string_view hwmon_path = "/sys/class/hwmon/hwmon0/temp1_input";
    constexpr std::string_view gpio_chip_name = "gpiochip0";
    constexpr unsigned int fault_led_offset = 26;
    constexpr double temp_threshold_celsius = 60.0;
}

class CarrierMonitor {
public:
    explicit CarrierMonitor(std::string_view chip_name)
        : chip_(std::string(chip_name)) {}

    [[nodiscard]] double read_temperature() const {
        if (!std::filesystem::exists(hwmon_path)) {
            throw std::runtime_error("Файл інтерфейсу hwmon не знайдено: " + std::string(hwmon_path));
        }

        std::ifstream file(std::string(hwmon_path));
        if (!file.is_open()) {
            throw std::runtime_error("Не вдалося відкрити sysfs файл температури");
        }

        long milli_celsius = 0;
        if (!(file >> milli_celsius)) {
            throw std::runtime_error("Помилка парсингу значення температури");
        }

        return static_cast<double>(milli_celsius) / 1000.0;
    }

    void set_fault_indicator(bool state) {
        auto line = chip_.get_line(fault_led_offset);
        line.request({
            "carrier-monitor-cpp",
            gpiod::line_request::DIRECTION_OUTPUT,
            0
        }, state ? 1 : 0);
        line.set_value(state ? 1 : 0);
        line.release();
    }

private:
    gpiod::chip chip_;
};

int main() {
    try {
        CarrierMonitor monitor(gpio_chip_name);
        const double current_temp = monitor.read_temperature();
        std::cout << "Поточна температура плати: " << current_temp << " °C\n";

        if (current_temp > temp_threshold_celsius) {
            std::cout << "УВАГА: Перегрів! Активація аварійного світлодіода (GPIO" << fault_led_offset << ")\n";
            monitor.set_fault_indicator(true);
        } else {
            std::cout << "Температурний режим у нормі.\n";
            monitor.set_fault_indicator(false);
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка моніторингу: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
