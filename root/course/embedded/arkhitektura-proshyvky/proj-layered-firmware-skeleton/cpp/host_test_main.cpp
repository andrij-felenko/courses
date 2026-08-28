// targets/host_test_main.cpp
#include <iostream>
#include <cassert>
#include <array>
#include "hal/hal_i2c.hpp"
#include "bsp/bsp_bme280.hpp"
#include "services/event_queue.hpp"
#include "app/app_telemetry.hpp"

class MockI2cBus : public hal::II2cBus {
public:
    MockI2cBus() {
        memory_[0xD0] = 0x60; // BME280 Chip ID
        memory_[0xF7 + 3] = 0x8A;
        memory_[0xF7 + 4] = 0x6E;
        memory_[0xF7 + 5] = 0x70;
    }

    std::expected<void, hal::I2cError> write_reg(uint8_t, uint8_t, 
                                                 std::span<const uint8_t>) override {
        return {};
    }

    std::expected<void, hal::I2cError> read_reg(uint8_t, uint8_t reg_addr, 
                                                std::span<uint8_t> data) override {
        for (size_t i = 0; i < data.size(); ++i) {
            data[i] = memory_[(reg_addr + i) & 0xFF];
        }
        return {};
    }

private:
    std::array<uint8_t, 256> memory_{};
};

int main() {
    MockI2cBus mock_bus;
    bsp::Bme280 sensor(mock_bus);
    assert(sensor.init() == true);

    services::EventQueue<16> queue;
    app::TelemetryCoordinator coordinator(sensor, queue, 35.0f);

    services::Event trigger{
        .type = services::EventType::SensorTrigger,
        .timestamp_ms = 1000
    };

    coordinator.process_event(trigger);

    auto alert = queue.pop();
    assert(alert.has_value());
    assert(alert->type == services::EventType::AlertThreshold);

    std::cout << "Unit test PASSED: C++ Coordinator executed seamlessly on Host PC!\n";
    return 0;
}
