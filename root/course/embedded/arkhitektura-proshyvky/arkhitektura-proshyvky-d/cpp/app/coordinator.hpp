// app/coordinator.hpp — координатор застосунку.
// Він єдиний знає всіх одразу: давачі, приймач подій, автомат режимів і
// вікно телеметрії. Знає — але лише через інтерфейси, отримані ззовні,
// тож у тесті на місце BME280 стає підробка, і бізнес-правила
// перевіряються без жодного шматка заліза.
#pragma once

#include "app/events.hpp"
#include "app/state_machine.hpp"
#include "app/telemetry.hpp"
#include "bsp/accelerometer.hpp"
#include "bsp/bme280.hpp"
#include "bsp/status_led.hpp"

namespace app {

class Coordinator {
public:
    struct Config {
        bsp::IEnvironmentSensor& environment;
        bsp::IAccelerometer*     accelerometer;   // nullptr припустимий
        bsp::StatusLed&          led;
        IEventSink&              events;
        ITelemetrySink*          telemetry;       // nullptr припустимий
        float                    temp_limit_c;
        float                    temp_hysteresis_c;
        float                    vibration_limit_g;
        hal::Millis              telemetry_window;
        std::uint32_t            fault_limit;
    };

    Coordinator(const Config& config, hal::Millis now);

    // Єдина точка входу з головного циклу: подія — рішення — дія.
    void dispatch(const SystemEvent& event);

    [[nodiscard]] State state() const noexcept { return fsm_.state(); }
    [[nodiscard]] std::uint32_t records_published() const noexcept { return published_; }

private:
    bool sample_sensors(hal::Millis now);
    void apply(Action action, hal::Millis now);
    void evaluate_thresholds(const bsp::Environment& env, float vibration_g,
                             hal::Millis now);

    Config          cfg_;
    StateMachine    fsm_;
    TelemetryWindow window_;
    bool            alarm_active_{false};
    std::uint32_t   published_{0};
};

} // namespace app
