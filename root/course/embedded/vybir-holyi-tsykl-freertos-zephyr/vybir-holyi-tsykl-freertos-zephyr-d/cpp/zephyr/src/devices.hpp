#pragma once

// Тонка обгортка над драйверною моделлю Zephyr. Вона нічого не приховує й
// нічого не додає: те саме struct device, лише замість цілих кодів помилок —
// std::expected, який неможливо мовчки проігнорувати.
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/sensor.h>

#include <expected>

namespace app {

enum class DeviceError { NotReady, FetchFailed, ChannelUnavailable, ConfigFailed };

class Sensor {
public:
    explicit constexpr Sensor(const device *dev) noexcept : dev_{dev} {}

    [[nodiscard]] std::expected<void, DeviceError> ready() const noexcept
    {
        if (!device_is_ready(dev_)) {
            return std::unexpected{DeviceError::NotReady};
        }
        return {};
    }

    // Одне вимірювання: вибірка й потрібний канал разом, бо порізно вони
    // не мають сенсу — sensor_channel_get віддає те, що взяв fetch.
    [[nodiscard]] std::expected<double, DeviceError> read(sensor_channel channel) const noexcept
    {
        if (sensor_sample_fetch(dev_) != 0) {
            return std::unexpected{DeviceError::FetchFailed};
        }
        sensor_value value{};
        if (sensor_channel_get(dev_, channel, &value) != 0) {
            return std::unexpected{DeviceError::ChannelUnavailable};
        }
        return sensor_value_to_double(&value);
    }

    [[nodiscard]] const char *name() const noexcept { return dev_->name; }

private:
    const device *dev_;
};

class Led {
public:
    explicit constexpr Led(const gpio_dt_spec &spec) noexcept : spec_{spec} {}

    [[nodiscard]] std::expected<void, DeviceError> configure() noexcept
    {
        if (!gpio_is_ready_dt(&spec_)) {
            return std::unexpected{DeviceError::NotReady};
        }
        if (gpio_pin_configure_dt(&spec_, GPIO_OUTPUT_INACTIVE) != 0) {
            return std::unexpected{DeviceError::ConfigFailed};
        }
        return {};
    }

    void set(bool on) noexcept { gpio_pin_set_dt(&spec_, on ? 1 : 0); }
    void toggle() noexcept { gpio_pin_toggle_dt(&spec_); }

private:
    gpio_dt_spec spec_;
};

constexpr const char *to_string(DeviceError e) noexcept
{
    switch (e) {
    case DeviceError::NotReady: return "пристрій не готовий";
    case DeviceError::FetchFailed: return "вибірка не вдалася";
    case DeviceError::ChannelUnavailable: return "канал недоступний";
    case DeviceError::ConfigFailed: return "не вдалося налаштувати вивід";
    }
    return "невідома помилка";
}

} // namespace app
