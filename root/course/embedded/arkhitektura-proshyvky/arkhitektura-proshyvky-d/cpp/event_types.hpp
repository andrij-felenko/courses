// event_types.hpp
#pragma once
#include <cstdint>
#include <variant>
#include <span>

namespace events {

enum class EventId : uint16_t {
    None = 0,
    Tick100ms,
    ButtonClick,
    SensorDataReady,
    AlarmOvertemp,
    CommsPacketRx
};

struct SensorPayload {
    float temp_c{0.0f};
    float pressure_kpa{0.0f};
};

struct PacketPayload {
    std::span<const uint8_t> buffer;
};

struct SystemEvent {
    EventId id{EventId::None};
    uint32_t timestamp_ms{0};
    std::variant<std::monostate, uint8_t, SensorPayload, PacketPayload> payload{};
};

} // namespace events
