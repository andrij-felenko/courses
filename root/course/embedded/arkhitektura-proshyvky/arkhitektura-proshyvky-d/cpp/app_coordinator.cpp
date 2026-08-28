// app/app_coordinator.cpp
#include "bsp/bsp_bme280.hpp"
#include "services/event_queue.hpp"

namespace app {

class TelemetryCoordinator {
public:
    TelemetryCoordinator(bsp::Bme280Driver& sensor, 
                         services::EventQueue<16>& queue, 
                         float temp_limit_c)
        : sensor_(sensor), queue_(queue), temp_limit_c_(temp_limit_c) {}

    void on_tick() {
        auto readings = sensor_.measure();
        if (readings.has_value() && readings->temperature_c > temp_limit_c_) {
            events::SystemEvent alert{
                .id = events::EventId::AlarmOvertemp,
                .timestamp_ms = 0,
                .payload = events::SensorPayload{
                    .temp_c = readings->temperature_c,
                    .pressure_kpa = readings->pressure_hpa / 10.0f
                }
            };
            queue_.push(alert);
        }
    }

private:
    bsp::Bme280Driver& sensor_;
    services::EventQueue<16>& queue_;
    float temp_limit_c_;
};

} // namespace app
