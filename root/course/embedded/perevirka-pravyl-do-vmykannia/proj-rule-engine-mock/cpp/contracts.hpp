#pragma once

#include <cstdint>

// Дві структури й два інтерфейси — уся межа між логікою правил і залізом.
// Рушій не знає ні про GPIO, ні про АЦП, ні про I2C: він бачить лише знімок
// стану на вході й виставляє стан приводів на виході. Саме тому той самий
// об'єктний файл збирається і в прошивку, і в стенд симуляції.

// Знімок стану системи на один момент часу.
struct SensorSnapshot {
    float temperature_c{20.0f};       // температура теплоносія, °C
    float pressure_bar{2.0f};         // тиск у гідроконтурі, бар
    bool flow_detected{true};         // крильчатка бачить протік
    bool emergency_stop_btn{false};   // натиснуто грибок аварійної зупинки
    bool sensor_fault{false};         // драйвер вимірювача повідомив про відмову
    std::uint32_t timestamp_ms{0};    // віртуальна або реальна мітка часу
};

// Команди на силову частину.
struct ActuatorState {
    bool heater_stage1{false};        // ТЕН 1 (6 кВт)
    bool heater_stage2{false};        // ТЕН 2 (6 кВт)
    bool circulation_pump{false};     // циркуляційна помпа
    bool alarm_siren{false};          // аварійна сигналізація
};

inline bool heaters_on(const ActuatorState& s) {
    return s.heater_stage1 || s.heater_stage2;
}

// Шина вимірювань: у прошивці — HAL, у стенді — модель або ін'єктор.
class ISensorSource {
public:
    virtual ~ISensorSource() = default;
    virtual SensorSnapshot read_snapshot() = 0;
};

// Стік команд: у прошивці — реальні ключі, у стенді — суха прогонка.
class IActuatorSink {
public:
    virtual ~IActuatorSink() = default;
    virtual void apply_commands(const ActuatorState& state, std::uint32_t time_ms) = 0;
};
