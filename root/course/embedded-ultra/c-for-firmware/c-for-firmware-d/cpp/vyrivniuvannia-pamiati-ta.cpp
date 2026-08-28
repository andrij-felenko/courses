#include <cstdint>
#include <cstddef>

// Щільно упакований C++ заголовок пакета телеметрії
struct [[gnu::packed]] TelemetryPacketHeader {
    uint8_t  node_id;
    uint32_t timestamp_ms;
    uint16_t packet_seq;
    uint16_t crc16;
};

static_assert(sizeof(TelemetryPacketHeader) == 9, "Розмір заголовка має бути рівно 9 байтів!");
