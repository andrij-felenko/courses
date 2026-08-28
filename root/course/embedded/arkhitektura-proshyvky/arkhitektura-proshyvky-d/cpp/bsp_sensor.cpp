// bsp_sensor.cpp — Приватна реалізація класу в C++
#include "bsp_sensor.hpp"

namespace bsp {

class Bme280Sensor final : public ISensor {
public:
    Bme280Sensor(uint8_t bus_id, uint8_t address)
        : bus_id_(bus_id), address_(address) {}

    bool init() override {
        // Ініціалізація регістрів датчика
        return true;
    }

    std::optional<SensorData> read_data() override {
        SensorData data{
            .temperature_c = 24.5f,
            .pressure_kpa = 101.3f
        };
        return data;
    }

private:
    uint8_t bus_id_;
    uint8_t address_;
    int16_t calib_t1_{0};
    int16_t calib_t2_{0};
};

std::unique_ptr<ISensor> create_environment_sensor(uint8_t bus_id, uint8_t i2c_address) {
    return std::make_unique<Bme280Sensor>(bus_id, i2c_address);
}

} // namespace bsp
