// packet.hpp
#pragma once
#include <cstdint>

struct NetworkPacket {
    uint32_t id;
#ifdef ENABLE_DIAGNOSTICS
    uint64_t timestamp;
#endif
    uint32_t payload_size;
};

void send_packet(const NetworkPacket& pkt);
