#include <bit>
#include <cstdint>
#include <span>
#include <optional>
#include <cstring>

struct PacketHeader {
    uint32_t sequence_id;
    uint16_t payload_length;
    uint16_t flags;
};

// Функція обміну байтів для 32-бітного числа
constexpr uint32_t byteswap32(uint32_t val) noexcept {
    return ((val & 0x000000FFu) << 24) |
           ((val & 0x0000FF00u) << 8)  |
           ((val & 0x00FF0000u) >> 8)  |
           ((val & 0xFF000000u) >> 24);
}

std::optional<PacketHeader> parse_network_header(std::span<const std::byte> raw_bytes) noexcept {
    if (raw_bytes.size() < sizeof(PacketHeader)) {
        return std::nullopt;
    }

    PacketHeader hdr{};
    std::memcpy(&hdr, raw_bytes.data(), sizeof(PacketHeader));

    // Якщо хост є Little-Endian, конвертуємо з Big-Endian мережі
    if constexpr (std::endian::native == std::endian::little) {
        hdr.sequence_id = byteswap32(hdr.sequence_id);
        hdr.payload_length = static_cast<uint16_t>((hdr.payload_length >> 8) | (hdr.payload_length << 8));
    }

    return hdr;
}
