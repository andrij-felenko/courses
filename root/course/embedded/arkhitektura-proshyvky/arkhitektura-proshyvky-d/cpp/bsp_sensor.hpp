// bsp_sensor.hpp — Ідіоматичний еквівалент на сучасному C++
#pragma once
#include <cstdint>
#include <optional>
#include <memory>

namespace bsp {

struct SensorData {
    float temperature_c{0.0f};
    float pressure_kpa{0.0f};
};

class ISensor {
public:
    virtual ~ISensor() = default;
    virtual bool init() = 0;
    virtual std::optional<SensorData> read_data() = 0;
};

// Фабрична функція, що повертає унікальний покажчик на інтерфейс
std::unique_ptr<ISensor> create_environment_sensor(uint8_t bus_id, uint8_t i2c_address);

} // namespace bsp
