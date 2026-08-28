#include <cstdint>
#include <array>
#include <span>
#include <bit>
#include <string>
#include <format>

namespace net {

inline constexpr std::size_t mac_address_len = 6;
inline constexpr std::size_t ethernet_header_len = 14;
inline constexpr std::size_t vlan_tag_len = 4;
inline constexpr std::size_t min_frame_len = 64;
inline constexpr std::size_t max_standard_frame_len = 1518;
inline constexpr std::size_t fcs_len = 4;

enum class ether_type : uint16_t {
    ipv4  = 0x0800,
    arp   = 0x0806,
    vlan  = 0x8100,
    ipv6  = 0x86DD,
    qinq  = 0x88A8,
    lldp  = 0x88CC,
    ptp   = 0x88F7
};

using mac_address = std::array<uint8_t, mac_address_len>;

#pragma pack(push, 1)
struct eth_header {
    mac_address dst_mac;
    mac_address src_mac;
    uint16_t    ethertype_be;

    [[nodiscard]] ether_type type() const noexcept {
        uint16_t host_val = (std::endian::native == std::endian::big)
            ? ethertype_be
            : std::byteswap(ethertype_be);
        return static_cast<ether_type>(host_val);
    }

    [[nodiscard]] bool is_multicast() const noexcept {
        return (dst_mac[0] & 0x01) != 0;
    }

    [[nodiscard]] bool is_broadcast() const noexcept {
        return dst_mac == mac_address{0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
    }

    [[nodiscard]] bool is_local_admin() const noexcept {
        return (dst_mac[0] & 0x02) != 0;
    }

    [[nodiscard]] std::string format_dst() const {
        return std::format("{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}",
            dst_mac[0], dst_mac[1], dst_mac[2], dst_mac[3], dst_mac[4], dst_mac[5]);
    }
};

struct vlan_header {
    uint16_t tpid_be;
    uint16_t tci_be;

    [[nodiscard]] uint16_t tci() const noexcept {
        return (std::endian::native == std::endian::big)
            ? tci_be
            : std::byteswap(tci_be);
    }

    [[nodiscard]] uint8_t pcp() const noexcept  { return static_cast<uint8_t>((tci() >> 13) & 0x07); }
    [[nodiscard]] bool dei() const noexcept     { return ((tci() >> 12) & 0x01) != 0; }
    [[nodiscard]] uint16_t vid() const noexcept { return tci() & 0x0FFF; }
};
#pragma pack(pop)

} // namespace net
