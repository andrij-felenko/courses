// app/events.hpp — подія системи.
// Там, де C бере union і сподівається на дисципліну програміста, C++ бере
// std::variant: дістати з події не те навантаження, яке в ній лежить,
// просто не вийде — перевірка альтернативи вбудована в тип.
#pragma once

#include "hal/clock.hpp"

#include <cstdint>
#include <span>
#include <string_view>
#include <variant>

namespace app {

enum class EventId : std::uint8_t {
    None = 0,
    Tick,
    ButtonClick,
    SensorDataReady,
    SensorFault,
    AlarmOvertemp,
    AlarmVibration,
    AlarmCleared,
    PacketReceived
};

struct ButtonPayload {
    std::uint8_t pin{0};
};

struct SensorPayload {
    float temperature_c{0.0F};
    float pressure_hpa{0.0F};
};

struct VibrationPayload {
    float peak_g{0.0F};
};

struct FaultPayload {
    std::uint8_t device_address{0};
    std::uint8_t error_code{0};
};

struct PacketPayload {
    std::span<const std::uint8_t> bytes;
};

using EventPayload = std::variant<std::monostate,
                                  ButtonPayload,
                                  SensorPayload,
                                  VibrationPayload,
                                  FaultPayload,
                                  PacketPayload>;

struct SystemEvent {
    EventId      id{EventId::None};
    hal::Millis  timestamp{};
    EventPayload payload{};
};

// Безпечний доступ до навантаження: nullptr, якщо в події лежить інше.
template <typename T>
[[nodiscard]] const T* payload_if(const SystemEvent& event) noexcept
{
    return std::get_if<T>(&event.payload);
}

// Куди складають подію. Черга — не єдиний можливий приймач: у тесті на
// це місце стає список, який просто запам'ятовує все, що сталося.
class IEventSink {
public:
    virtual ~IEventSink() = default;

    // false — приймач переповнений і подію втрачено.
    virtual bool post(const SystemEvent& event) = 0;
};

[[nodiscard]] constexpr std::string_view to_string(EventId id) noexcept
{
    switch (id) {
    case EventId::None:            return "NONE";
    case EventId::Tick:            return "TICK";
    case EventId::ButtonClick:     return "BUTTON";
    case EventId::SensorDataReady: return "SENSOR_DATA";
    case EventId::SensorFault:     return "SENSOR_FAULT";
    case EventId::AlarmOvertemp:   return "ALARM_TEMP";
    case EventId::AlarmVibration:  return "ALARM_VIB";
    case EventId::AlarmCleared:    return "ALARM_CLEARED";
    case EventId::PacketReceived:  return "PACKET_RX";
    }
    return "?";
}

} // namespace app
