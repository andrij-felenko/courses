#include <variant>
#include <cstdint>

struct SensorData {
    uint32_t timestamp;
    float temperature;
};

struct SensorError {
    uint8_t error_code;
};

using SensorResult = std::variant<SensorData, SensorError>;

void handle_sensor(const SensorResult& res) {
    // Безвинятковий підхід у Embedded C++
    if (const auto* data = std::get_if<SensorData>(&res)) {
        // Успішна обробка даних датчика
        (void)data->temperature;
    } else if (const auto* err = std::get_if<SensorError>(&res)) {
        // Обробка коду помилки
        (void)err->error_code;
    }
}
