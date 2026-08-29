// app/app_telemetry.hpp — чиста бізнес-політика вузла телеметрії.
// Не знає ні про I2C1, ні про ніжку MOSFET: бачить драйвер давача й вихід для подій.
#pragma once

#include <chrono>
#include <cstdint>
#include <optional>

#include "bsp/bsp_bme280.hpp"
#include "services/dispatcher.hpp"

namespace app {

class TelemetryCoordinator final : public services::IEventHandler {
public:
    // Скільки невдалих опитувань поспіль дозволено, перш ніж вузол оголосить
    // давач несправним.
    static constexpr std::uint8_t kFaultLimit = 3;

    TelemetryCoordinator(bsp::Bme280& sensor, services::IEventSink& sink, float alert_threshold_c,
                         std::uint16_t sample_period_ticks) noexcept
        : sensor_(sensor),
          sink_(sink),
          alert_threshold_c_(alert_threshold_c),
          sample_period_ticks_(sample_period_ticks == 0 ? 1 : sample_period_ticks)
    {
    }

    // Тик таймера накопичує період, тригер опитує давач негайно;
    // решта типів подій цього координатора не обходить.
    void on_event(const services::Event& evt) override;

    // Після успішного перезапуску живлення лічильник відмов треба обнулити,
    // інакше наступна ж невдача одразу дасть нову тривогу.
    void notify_recovered() noexcept { consecutive_failures_ = 0; }

    std::optional<bsp::SensorReading> last_reading() const noexcept { return last_reading_; }

    std::uint32_t samples_taken() const noexcept { return samples_taken_; }
    std::uint32_t alerts_raised() const noexcept { return alerts_raised_; }
    std::uint32_t faults_raised() const noexcept { return faults_raised_; }
    std::uint8_t consecutive_failures() const noexcept { return consecutive_failures_; }

    static constexpr services::EventMask subscription()
    {
        return services::EventMask{services::EventType::TimerTick,
                                   services::EventType::SensorTrigger};
    }

private:
    void take_sample(std::chrono::milliseconds timestamp);

    bsp::Bme280& sensor_;
    services::IEventSink& sink_;
    float alert_threshold_c_;
    std::uint16_t sample_period_ticks_;
    std::uint16_t ticks_since_sample_{0};
    std::uint8_t consecutive_failures_{0};

    std::optional<bsp::SensorReading> last_reading_{};
    std::uint32_t samples_taken_{0};
    std::uint32_t alerts_raised_{0};
    std::uint32_t faults_raised_{0};
};

}  // namespace app
