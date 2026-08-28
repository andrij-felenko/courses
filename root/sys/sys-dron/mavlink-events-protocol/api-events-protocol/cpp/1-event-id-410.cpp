#include <cstdint>
#include <array>

// Ідіоматична типізована структура кадру EVENT
struct alignas(1) MavlinkEventMessage {
    uint32_t              id{0};
    uint32_t              eventTimeBootMs{0};
    uint16_t              sequence{0};
    uint8_t               destinationComponent{0};
    uint8_t               destinationSystem{0};
    uint8_t               logLevels{0};
    std::array<uint8_t, 40> arguments{};
};
