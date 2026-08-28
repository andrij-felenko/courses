#include <cstdint>
#include <array>
#include <span>
#include <vector>
#include <bit>
#include <cstring>

namespace net {

[[nodiscard]] std::vector<uint8_t>
craft_frame(mac_address dst, mac_address src,
            uint16_t vlan_id, ether_type type,
            std::span<const uint8_t> payload) {
    std::vector<uint8_t> buffer;
    buffer.reserve(64 + payload.size());

    buffer.insert(buffer.end(), dst.begin(), dst.end());
    buffer.insert(buffer.end(), src.begin(), src.end());

    if (vlan_id >= 1 && vlan_id <= 4094) {
        buffer.push_back(0x81);
        buffer.push_back(0x00);
        buffer.push_back(static_cast<uint8_t>((vlan_id >> 8) & 0x0F));
        buffer.push_back(static_cast<uint8_t>(vlan_id & 0xFF));
    }

    auto raw_type = static_cast<uint16_t>(type);
    buffer.push_back(static_cast<uint8_t>((raw_type >> 8) & 0xFF));
    buffer.push_back(static_cast<uint8_t>(raw_type & 0xFF));

    buffer.insert(buffer.end(), payload.begin(), payload.end());

    /* Доповнення нулями до мінімального розміру 60 байтів */
    if (buffer.size() < 60) {
        buffer.resize(60, 0x00);
    }

    /* Обчислення FCS */
    uint32_t crc = calculate_crc32(buffer);
    buffer.push_back(static_cast<uint8_t>(crc & 0xFF));
    buffer.push_back(static_cast<uint8_t>((crc >> 8) & 0xFF));
    buffer.push_back(static_cast<uint8_t>((crc >> 16) & 0xFF));
    buffer.push_back(static_cast<uint8_t>((crc >> 24) & 0xFF));

    return buffer;
}

} // namespace net
