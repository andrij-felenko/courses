// app/coordinator.cpp — бізнес-правила логера вібрації.
// Найнижче, куди зазирає цей файл, — заголовок драйвера. Ані регістра,
// ані вендорного виклику тут немає, і саме тому заміна STM32 на ESP32
// не змінює в ньому жодного рядка.
//
// Рішення координатор не виконує сам, а публікує подіями: аварія стає
// подією в черзі й повертається сюди наступним обертом циклу. Завдяки
// цьому будь-хто — журнал, радіомодуль, дисплей — може її почути, не
// будучи згаданим у цьому файлі.
#include "app/coordinator.hpp"

namespace app {

Coordinator::Coordinator(const Config& config, hal::Millis now)
    : cfg_{config},
      fsm_{config.fault_limit},
      window_{config.telemetry_window, now}
{
    if (cfg_.temp_hysteresis_c <= 0.0F) {
        cfg_.temp_hysteresis_c = 1.0F;
    }
}

void Coordinator::dispatch(const SystemEvent& event)
{
    apply(fsm_.dispatch(event), event.timestamp);

    // Індикація живе на тіку: миготіння не має залежати від того, чи
    // встиг давач відповісти цього оберту.
    if (event.id == EventId::Tick) {
        cfg_.led.tick(event.timestamp);
    }
}

void Coordinator::apply(Action action, hal::Millis now)
{
    switch (action) {

    case Action::StartSampling:
        cfg_.led.set_mode(bsp::LedMode::BlinkSlow);
        window_.restart(now);
        break;

    case Action::StopSampling:
        cfg_.led.set_mode(bsp::LedMode::Off);
        break;

    case Action::SampleSensors:
        static_cast<void>(sample_sensors(now));
        break;

    case Action::RaiseAlarm:
        cfg_.led.set_mode(bsp::LedMode::BlinkFast);
        break;

    case Action::ClearAlarm:
    case Action::Recover:
        cfg_.led.set_mode(bsp::LedMode::BlinkSlow);
        break;

    case Action::EnterFault:
        // Давач мовчить. Світлодіод горить рівно — це видно здалеку й
        // відрізняється від миготіння штатної роботи.
        cfg_.led.set_mode(bsp::LedMode::On);
        alarm_active_ = false;
        break;

    case Action::None:
        break;
    }
}

bool Coordinator::sample_sensors(hal::Millis now)
{
    const auto env = cfg_.environment.measure();
    if (!env) {
        window_.add_fault();
        static_cast<void>(cfg_.events.post(SystemEvent{
            .id = EventId::SensorFault,
            .timestamp = now,
            .payload = FaultPayload{
                .device_address = 0,
                .error_code = static_cast<std::uint8_t>(env.error()),
            },
        }));
        return false;
    }

    float vibration_g = 0.0F;
    if (cfg_.accelerometer != nullptr) {
        const auto sample = cfg_.accelerometer->read();
        if (!sample) {
            // Свіжу температуру з торішньою вібрацією не змішуємо:
            // цикл чесно вважається невдалим цілком.
            window_.add_fault();
            static_cast<void>(cfg_.events.post(SystemEvent{
                .id = EventId::SensorFault,
                .timestamp = now,
                .payload = FaultPayload{
                    .device_address = 1,
                    .error_code = static_cast<std::uint8_t>(sample.error()),
                },
            }));
            return false;
        }
        vibration_g = sample->vibration_g();
    }

    window_.add(Measurement{
        .temperature_c = env->temperature_c,
        .humidity_rh   = env->humidity_rh,
        .pressure_hpa  = env->pressure_hpa,
        .vibration_g   = vibration_g,
    });

    static_cast<void>(cfg_.events.post(SystemEvent{
        .id = EventId::SensorDataReady,
        .timestamp = now,
        .payload = SensorPayload{
            .temperature_c = env->temperature_c,
            .pressure_hpa  = env->pressure_hpa,
        },
    }));

    evaluate_thresholds(*env, vibration_g, now);

    if (window_.elapsed(now)) {
        if (const auto record = window_.close(now);
            record && cfg_.telemetry != nullptr) {
            cfg_.telemetry->publish(*record);
            ++published_;
        }
    }
    return true;
}

void Coordinator::evaluate_thresholds(const bsp::Environment& env,
                                      float vibration_g, hal::Millis now)
{
    const bool too_hot = env.temperature_c > cfg_.temp_limit_c;
    const bool shaking = vibration_g > cfg_.vibration_limit_g;

    if (!alarm_active_) {
        if (too_hot) {
            alarm_active_ = true;
            static_cast<void>(cfg_.events.post(SystemEvent{
                .id = EventId::AlarmOvertemp,
                .timestamp = now,
                .payload = SensorPayload{
                    .temperature_c = env.temperature_c,
                    .pressure_hpa  = env.pressure_hpa,
                },
            }));
        } else if (shaking) {
            alarm_active_ = true;
            static_cast<void>(cfg_.events.post(SystemEvent{
                .id = EventId::AlarmVibration,
                .timestamp = now,
                .payload = VibrationPayload{.peak_g = vibration_g},
            }));
        }
        return;
    }

    // Тривога знімається лише коли температура впала нижче за поріг на
    // гістерезис: без цього логер на межі 65.0 °C сипав би подіями
    // сотнями разів на хвилину.
    const bool cooled = env.temperature_c < (cfg_.temp_limit_c - cfg_.temp_hysteresis_c);
    if (cooled && !shaking) {
        alarm_active_ = false;
        static_cast<void>(cfg_.events.post(SystemEvent{
            .id = EventId::AlarmCleared,
            .timestamp = now,
        }));
    }
}

} // namespace app
