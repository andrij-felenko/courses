#include <cstdint>
#include <span>
#include <cstring>
#include <netinet/in.h>

namespace embedded::dns {

struct [[nodiscard]] DnsSpoofer {
    static constexpr uint8_t FlagsHigh = 0x81; // QR=1, AA=1
    static constexpr uint8_t FlagsLow  = 0x80; // RA=1, RCODE=0
    static constexpr uint32_t TtlSeconds = 10;

    static size_t spoofResponse(std::span<uint8_t> packet, size_t queryLen, uint32_t localIpNetworkOrder) noexcept {
        if (queryLen < 12 || packet.size() < queryLen + 16) {
            return 0;
        }

        packet[2] = FlagsHigh;
        packet[3] = FlagsLow;
        packet[6] = 0x00; packet[7] = 0x01; // ANCOUNT = 1
        packet[8] = 0x00; packet[9] = 0x00; // NSCOUNT = 0
        packet[10] = 0x00; packet[11] = 0x00; // ARCOUNT = 0

        size_t offset = queryLen;
        packet[offset++] = 0xC0; packet[offset++] = 0x0C; // Pointer to QNAME
        packet[offset++] = 0x00; packet[offset++] = 0x01; // Type A
        packet[offset++] = 0x00; packet[offset++] = 0x01; // Class IN
        packet[offset++] = 0x00; packet[offset++] = 0x00;
        packet[offset++] = 0x00; packet[offset++] = static_cast<uint8_t>(TtlSeconds);
        packet[offset++] = 0x00; packet[offset++] = 0x04; // Length 4

        std::memcpy(&packet[offset], &localIpNetworkOrder, sizeof(localIpNetworkOrder));
        offset += sizeof(localIpNetworkOrder);

        return offset;
    }
};

} // namespace embedded::dns
