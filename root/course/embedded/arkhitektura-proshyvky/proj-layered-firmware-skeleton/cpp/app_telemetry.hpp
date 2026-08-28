// app/app_telemetry.hpp
#pragma once
#include "bsp/bsp_bme280.hpp"
#include "services/event_queue.hpp"

namespace app {

class TelemetryCoordinator {
public:
    TelemetryCoordinator(bsp::Bme280& sensor, services::EventQueue<16>& queue, float threshold_c)
        : sensor_(sensor), queue_(queue), alert_threshold_c_(threshold_c) {}

    void process_event(const services::Event& evt) {
        if (evt.type == services::EventType::SensorTrigger) {
            auto reading = sensor_.read();
            if (reading) {
                if (reading->temperature_c > alert_threshold_c_) {
                    services::Event alert{
                        .type = services::EventType::AlertThreshold,
                        .timestamp_ms = evt.timestamp_ms,
                        .payload = {.sensor_val = reading->temperature_c}
                    };
                    queue_.push(alert);
                }
            }
        }
    }

private:
    bsp::Bme280& sensor_;
    services::EventQueue<16>& queue_;
    float alert_threshold_c_;
};

} // namespace app
