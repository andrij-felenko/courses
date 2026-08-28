#include <variant>
#include <array>

struct TemperatureSensor {
    [[nodiscard]] float read() const noexcept { return 25.4f; }
};

struct PressureSensor {
    [[nodiscard]] float read() const noexcept { return 1013.25f; }
};

using SensorVariant = std::variant<TemperatureSensor, PressureSensor>;

float sample_sensor(const SensorVariant& s) noexcept {
    return std::visit([](const auto& sensor) noexcept {
        return sensor.read();
    }, s);
}
