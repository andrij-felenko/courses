// include/sensor_driver.hpp (C++ RAII Wrapper)
#pragma once

#include <expected>
#include <string_view>
#include <chrono>
#include "sensor_driver.h"

namespace sensors {

class EnvironmentSensor {
public:
    EnvironmentSensor() {
        const esp_err_t err = sensor_driver_init();
        is_initialized_ = (err == ESP_OK);
    }

    ~EnvironmentSensor() {
        if (is_initialized_) {
            sensor_driver_deinit();
        }
    }

    // Заборона копіювання апаратного ресурсу
    EnvironmentSensor(const EnvironmentSensor&) = delete;
    EnvironmentSensor& operator=(const EnvironmentSensor&) = delete;

    // Підтримка переміщення (move semantics)
    EnvironmentSensor(EnvironmentSensor&& other) noexcept
        : is_initialized_(other.is_initialized_) {
        other.is_initialized_ = false;
    }

    EnvironmentSensor& operator=(EnvironmentSensor&& other) noexcept {
        if (this != &other) {
            if (is_initialized_) {
                sensor_driver_deinit();
            }
            is_initialized_ = other.is_initialized_;
            other.is_initialized_ = false;
        }
        return *this;
    }

    [[nodiscard]] std::expected<sensor_reading_t, esp_err_t> read() const {
        if (!is_initialized_) {
            return std::unexpected(ESP_ERR_INVALID_STATE);
        }
        sensor_reading_t data{};
        const esp_err_t err = sensor_driver_read(&data);
        if (err != ESP_OK) {
            return std::unexpected(err);
        }
        return data;
    }

    [[nodiscard]] bool is_ready() const noexcept {
        return is_initialized_;
    }

private:
    bool is_initialized_{false};
};

} // namespace sensors
