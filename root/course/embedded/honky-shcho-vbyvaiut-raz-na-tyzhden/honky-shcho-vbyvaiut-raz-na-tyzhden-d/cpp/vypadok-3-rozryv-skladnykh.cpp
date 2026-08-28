#include <cstdint>
#include <span>

struct PacketDescriptor {
    const std::uint8_t *data{nullptr};
    std::uint16_t length{0};
    std::uint16_t flags{0};
};

inline volatile PacketDescriptor g_current_packet{};
