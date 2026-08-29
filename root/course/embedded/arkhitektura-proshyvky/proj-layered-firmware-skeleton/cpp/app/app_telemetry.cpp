// app/app_telemetry.cpp
#include "app/app_telemetry.hpp"

#include <limits>

namespace app {

void TelemetryCoordinator::take_sample(std::chrono::milliseconds timestamp)
{
    const std::optional<bsp::SensorReading> reading = sensor_.read();

    if (!reading) {
        // Крок 3 трасування: політику реакції на збій ухвалює саме цей шар.
        if (consecutive_failures_ < std::numeric_limits<std::uint8_t>::max()) {
            ++consecutive_failures_;
        }
        if (consecutive_failures_ >= kFaultLimit) {
            sink_.publish(services::Event{
                .type = services::EventType::SensorFault,
                .timestamp = timestamp,
                .payload = static_cast<std::int32_t>(consecutive_failures_),
            });
            ++faults_raised_;
            // Лічильник не обнуляємо тут: його зніме служба живлення, коли справді
            // перезапустить давач. Інакше тривога загубиться в циклі.
        }
        return;
    }

    consecutive_failures_ = 0;
    last_reading_ = reading;
    ++samples_taken_;

    if (reading->temperature_c > alert_threshold_c_) {
        sink_.publish(services::Event{
            .type = services::EventType::AlertThreshold,
            .timestamp = timestamp,
            .payload = reading->temperature_c,
        });
        ++alerts_raised_;
    }
}

void TelemetryCoordinator::on_event(const services::Event& evt)
{
    switch (evt.type) {
        case services::EventType::TimerTick:
            ++ticks_since_sample_;
            if (ticks_since_sample_ >= sample_period_ticks_) {
                ticks_since_sample_ = 0;
                take_sample(evt.timestamp);
            }
            break;

        case services::EventType::SensorTrigger:
            ticks_since_sample_ = 0;
            take_sample(evt.timestamp);
            break;

        default:
            // Тривога, несправність, звільнення передавача — не наша справа.
            break;
    }
}

}  // namespace app
