#include <cstdint>
#include <cstring>
#include <span>
#include <optional>
#include <bit>

struct Ipv4Header {
    uint8_t  version{};
    uint8_t  ihl_bytes{};
    uint8_t  tos{};
    uint16_t total_length{};
    uint16_t packet_id{};
    uint8_t  ttl{};
    uint8_t  protocol{};
    uint16_t header_checksum{};
    uint32_t src_ip{};
    uint32_t dst_ip{};
};

uint16_t compute_rfc1071_checksum(std::span<const std::byte> data) noexcept {
    uint32_t sum = 0;
    const size_t word_count = data.size() / 2;

    for (size_t i = 0; i < word_count; ++i) {
        uint16_t word{};
        std::memcpy(&word, data.data() + i * 2, sizeof(uint16_t));
        sum += word;
    }

    if (data.size() % 2 != 0) {
        uint8_t odd_byte = static_cast<uint8_t>(data.back());
        sum += odd_byte;
    }

    while (sum >> 16) {
        sum = (sum & 0xFFFFu) + (sum >> 16);
    }

    return static_cast<uint16_t>(~sum);
}

std::optional<Ipv4Header> parse_ipv4_header(std::span<const std::byte> packet) noexcept {
    if (packet.size() < 20) {
        return std::nullopt;
    }

    uint8_t ver_ihl = static_cast<uint8_t>(packet[0]);
    uint8_t version = ver_ihl >> 4;
    uint8_t ihl_words = ver_ihl & 0x0F;
    size_t header_len = static_cast<size_t>(ihl_words) * 4;

    if (version != 4 || header_len < 20 || packet.size() < header_len) {
        return std::nullopt;
    }

    // Перевірка цілісності контрольної суми
    if (compute_rfc1071_checksum(packet.subspan(0, header_len)) != 0) {
        return std::nullopt; // Пакет пошкоджений
    }

    Ipv4Header hdr{};
    hdr.version = version;
    hdr.ihl_bytes = static_cast<uint8_t>(header_len);
    hdr.tos = static_cast<uint8_t>(packet[1]);
    std::memcpy(&hdr.total_length, packet.data() + 2, 2);
    std::memcpy(&hdr.packet_id, packet.data() + 4, 2);
    hdr.ttl = static_cast<uint8_t>(packet[8]);
    hdr.protocol = static_cast<uint8_t>(packet[9]);
    std::memcpy(&hdr.header_checksum, packet.data() + 10, 2);
    std::memcpy(&hdr.src_ip, packet.data() + 12, 4);
    std::memcpy(&hdr.dst_ip, packet.data() + 16, 4);

    return hdr;
}
