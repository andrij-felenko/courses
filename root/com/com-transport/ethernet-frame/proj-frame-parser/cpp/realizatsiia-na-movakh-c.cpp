#include <cstdint>
#include <array>
#include <span>
#include <string>
#include <vector>
#include <expected>
#include <format>
#include <bit>

namespace net {

inline constexpr std::size_t mac_len = 6;
inline constexpr uint16_t ethertype_vlan = 0x8100;
inline constexpr uint16_t ethertype_qinq = 0x88A8;

using mac_address = std::array<uint8_t, mac_len>;

enum class parse_error {
    buffer_too_small,
    truncated_vlan_header,
    missing_fcs,
    checksum_mismatch
};

struct vlan_info {
    uint16_t vid{0};
    uint8_t  pcp{0};
    bool     dei{false};
};

struct ethernet_frame {
    mac_address dst_mac{};
    mac_address src_mac{};
    std::vector<vlan_info> vlans{};
    uint16_t ethertype{0};
    std::span<const uint8_t> payload{};
    bool fcs_verified{false};

    [[nodiscard]] std::string format_dst_mac() const {
        return std::format("{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}",
            dst_mac[0], dst_mac[1], dst_mac[2], dst_mac[3], dst_mac[4], dst_mac[5]);
    }
};

/* Генерація таблиці CRC-32 під час компіляції (C++20 consteval) */
consteval auto generate_crc32_table() {
    std::array<uint32_t, 256> table{};
    constexpr uint32_t polynomial = 0xEDB88320u;
    for (uint32_t i = 0; i < 256; ++i) {
        uint32_t crc = i;
        for (int j = 0; j < 8; ++j) {
            if (crc & 1)
                crc = (crc >> 1) ^ polynomial;
            else
                crc >>= 1;
        }
        table[i] = crc;
    }
    return table;
}

inline constexpr auto crc32_table = generate_crc32_table();

[[nodiscard]] constexpr uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFFu;
    for (uint8_t byte : data) {
        uint8_t table_idx = static_cast<uint8_t>((crc ^ byte) & 0xFF);
        crc = (crc >> 8) ^ crc32_table[table_idx];
    }
    return crc ^ 0xFFFFFFFFu;
}

[[nodiscard]] std::expected<ethernet_frame, parse_error>
parse_frame(std::span<const uint8_t> buffer, bool has_fcs = false) noexcept {
    if (buffer.size() < 14)
        return std::unexpected(parse_error::buffer_too_small);

    ethernet_frame frame;
    std::copy_n(buffer.data(), mac_len, frame.dst_mac.begin());
    std::copy_n(buffer.data() + mac_len, mac_len, frame.src_mac.begin());

    std::size_t offset = 12;

    /* Ітеративне зняття тегів 802.1Q / 802.1ad */
    while (offset + 4 <= buffer.size()) {
        uint16_t tag_type = static_cast<uint16_t>((buffer[offset] << 8) | buffer[offset + 1]);
        if (tag_type != ethertype_vlan && tag_type != ethertype_qinq)
            break;

        uint16_t tci = static_cast<uint16_t>((buffer[offset + 2] << 8) | buffer[offset + 3]);
        frame.vlans.push_back(vlan_info{
            .vid = static_cast<uint16_t>(tci & 0x0FFF),
            .pcp = static_cast<uint8_t>((tci >> 13) & 0x07),
            .dei = ((tci >> 12) & 0x01) != 0
        });
        offset += 4;
    }

    if (offset + 2 > buffer.size())
        return std::unexpected(parse_error::truncated_vlan_header);

    frame.ethertype = static_cast<uint16_t>((buffer[offset] << 8) | buffer[offset + 1]);
    offset += 2;

    /* Обробка IEEE 802.3 LLC/SNAP */
    if (frame.ethertype <= 1500) {
        if (offset + 8 <= buffer.size() &&
            buffer[offset] == 0xAA && buffer[offset + 1] == 0xAA && buffer[offset + 2] == 0x03) {
            frame.ethertype = static_cast<uint16_t>((buffer[offset + 6] << 8) | buffer[offset + 7]);
            offset += 8;
        }
    }

    std::size_t payload_end = buffer.size();
    if (has_fcs) {
        if (buffer.size() < offset + 4)
            return std::unexpected(parse_error::missing_fcs);
        payload_end -= 4;

        uint32_t expected_crc = calculate_crc32(buffer.subspan(0, payload_end));
        uint32_t actual_crc = static_cast<uint32_t>(buffer[payload_end]) |
                             (static_cast<uint32_t>(buffer[payload_end + 1]) << 8) |
                             (static_cast<uint32_t>(buffer[payload_end + 2]) << 16) |
                             (static_cast<uint32_t>(buffer[payload_end + 3]) << 24);

        if (expected_crc != actual_crc)
            return std::unexpected(parse_error::checksum_mismatch);

        frame.fcs_verified = true;
    } else {
        frame.fcs_verified = true;
    }

    frame.payload = buffer.subspan(offset, payload_end - offset);
    return frame;
}

} // namespace net
