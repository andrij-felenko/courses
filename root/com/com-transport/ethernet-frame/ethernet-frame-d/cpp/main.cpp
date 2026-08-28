#include <cstdint>
#include <array>
#include <span>
#include <optional>
#include <bit>

namespace net {

inline constexpr std::size_t mac_size = 6;
inline constexpr std::size_t eth_header_size = 14;
inline constexpr uint16_t ethertype_vlan = 0x8100;

struct parsed_eth_info {
    std::array<uint8_t, mac_size> dst_mac{};
    std::array<uint8_t, mac_size> src_mac{};
    uint16_t ethertype{0};
    std::span<const uint8_t> payload{};
};

[[nodiscard]] std::optional<parsed_eth_info>
parse_ethernet(std::span<const uint8_t> frame_bytes) noexcept {
    if (frame_bytes.size() < eth_header_size)
        return std::nullopt;

    parsed_eth_info info;
    std::copy_n(frame_bytes.data(), mac_size, info.dst_mac.begin());
    std::copy_n(frame_bytes.data() + mac_size, mac_size, info.src_mac.begin());

    std::size_t offset = 12;
    uint16_t proto = static_cast<uint16_t>((frame_bytes[offset] << 8) | frame_bytes[offset + 1]);
    offset += 2;

    /* Розгортання тега 802.1Q */
    if (proto == ethertype_vlan) {
        if (frame_bytes.size() < offset + 4)
            return std::nullopt;
        offset += 2; // Пропускаємо TCI
        proto = static_cast<uint16_t>((frame_bytes[offset] << 8) | frame_bytes[offset + 1]);
        offset += 2;
    }

    info.ethertype = proto;
    info.payload = frame_bytes.subspan(offset);
    return info;
}

} // namespace net
