#include <cstdint>
#include <array>

#pragma pack(push, 1)
struct ProxyHeaderV2 {
    std::array<uint8_t, 12> sig;
    uint8_t ver_cmd;
    uint8_t fam_tr;
    uint16_t len;
    union AddressUnion {
        struct IPv4Data {
            uint32_t src_addr;
            uint32_t dst_addr;
            uint16_t src_port;
            uint16_t dst_port;
        } ipv4;
        struct IPv6Data {
            std::array<uint8_t, 16> src_addr;
            std::array<uint8_t, 16> dst_addr;
            uint16_t src_port;
            uint16_t dst_port;
        } ipv6;
        struct UnixData {
            std::array<uint8_t, 108> src_addr;
            std::array<uint8_t, 108> dst_addr;
        } unix_sock;
    } addr;
};
#pragma pack(pop)
