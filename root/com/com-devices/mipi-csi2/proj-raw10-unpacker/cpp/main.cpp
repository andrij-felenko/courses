#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>
#include <expected>
#include <array>

namespace mipi::csi2 {

constexpr uint8_t DT_RAW10 = 0x2B;
constexpr uint16_t CRC16_CCITT_POLY = 0x1021;

enum class ParseError {
    BufferTooSmall,
    InvalidDataType,
    EccUncorrectable,
    CrcMismatch
};

struct PacketHeader {
    uint8_t virtual_channel;
    uint8_t data_type;
    uint16_t word_count;
    bool ecc_corrected;
};

// Обчислення бітів паритету Хеммінга для 24-бітного заголовка
constexpr uint8_t calculate_ecc(uint32_t data24) noexcept {
    auto bit = [data24](int n) -> uint32_t { return (data24 >> n) & 1U; };
    uint8_t p0 = bit(0)^bit(1)^bit(2)^bit(4)^bit(5)^bit(7)^bit(8)^bit(10)^bit(11)^bit(13)^bit(14)^bit(16)^bit(20)^bit(21)^bit(23);
    uint8_t p1 = bit(0)^bit(1)^bit(3)^bit(4)^bit(6)^bit(7)^bit(9)^bit(10)^bit(12)^bit(13)^bit(15)^bit(17)^bit(20)^bit(22)^bit(23);
    uint8_t p2 = bit(0)^bit(2)^bit(3)^bit(5)^bit(6)^bit(7)^bit(11)^bit(12)^bit(13)^bit(18)^bit(19)^bit(20)^bit(22)^bit(23);
    uint8_t p3 = bit(1)^bit(2)^bit(3)^bit(8)^bit(9)^bit(10)^bit(11)^bit(12)^bit(13)^bit(14)^bit(15)^bit(18)^bit(19)^bit(21)^bit(22)^bit(23);
    uint8_t p4 = bit(4)^bit(5)^bit(6)^bit(7)^bit(8)^bit(9)^bit(10)^bit(11)^bit(12)^bit(13)^bit(14)^bit(15)^bit(16)^bit(17)^bit(21)^bit(22)^bit(23);
    uint8_t p5 = bit(16)^bit(17)^bit(18)^bit(19)^bit(20)^bit(21)^bit(22)^bit(23);

    return static_cast<uint8_t>(p0 | (p1 << 1) | (p2 << 2) | (p3 << 3) | (p4 << 4) | (p5 << 5));
}

// Парсер та коректор заголовка
std::expected<PacketHeader, ParseError> parse_header(std::span<const uint8_t, 4> raw) noexcept {
    uint32_t data24 = static_cast<uint32_t>(raw[0]) |
                      (static_cast<uint32_t>(raw[1]) << 8) |
                      (static_cast<uint32_t>(raw[2]) << 16);
    uint8_t rx_ecc = raw[3] & 0x3F;
    uint8_t calc_ecc = calculate_ecc(data24);
    uint8_t syndrome = rx_ecc ^ calc_ecc;

    bool corrected = false;
    if (syndrome != 0) {
        constexpr std::array<uint8_t, 64> syndrome_lut = [] {
            std::array<uint8_t, 64> lut{};
            lut[0x07] = 0;  lut[0x0B] = 1;  lut[0x0D] = 2;  lut[0x0E] = 3;
            lut[0x13] = 4;  lut[0x15] = 5;  lut[0x16] = 6;  lut[0x19] = 7;
            lut[0x1A] = 8;  lut[0x1C] = 9;  lut[0x23] = 10; lut[0x25] = 11;
            lut[0x26] = 12; lut[0x29] = 13; lut[0x2A] = 14; lut[0x2C] = 15;
            lut[0x31] = 16; lut[0x32] = 17; lut[0x34] = 18; lut[0x38] = 19;
            lut[0x1F] = 20; lut[0x2F] = 21; lut[0x37] = 22; lut[0x3B] = 23;
            return lut;
        }();

        if (syndrome <= 0x3F && (syndrome == 0x01 || syndrome == 0x02 || syndrome == 0x04 ||
                                 syndrome == 0x08 || syndrome == 0x10 || syndrome == 0x20)) {
            corrected = true;
        } else if (syndrome <= 0x3F && syndrome_lut[syndrome] != 0) {
            uint8_t bit_idx = syndrome_lut[syndrome];
            data24 ^= (1U << bit_idx);
            corrected = true;
        } else {
            return std::unexpected(ParseError::EccUncorrectable);
        }
    }

    return PacketHeader{
        .virtual_channel = static_cast<uint8_t>((data24 >> 6) & 0x03),
        .data_type = static_cast<uint8_t>(data24 & 0x3F),
        .word_count = static_cast<uint16_t>((data24 >> 8) & 0xFFFF),
        .ecc_corrected = corrected
    };
}

// Розрахунок CRC-16-CCITT
uint16_t calculate_crc16(std::span<const uint8_t> payload) noexcept {
    uint16_t crc = 0xFFFF;
    for (uint8_t byte : payload) {
        crc ^= static_cast<uint16_t>(static_cast<uint16_t>(byte) << 8);
        for (int b = 0; b < 8; ++b) {
            if (crc & 0x8000) {
                crc = static_cast<uint16_t>((crc << 1) ^ CRC16_CCITT_POLY);
            } else {
                crc = static_cast<uint16_t>(crc << 1);
            }
        }
    }
    return crc;
}

// Розпакування RAW10 пакета в контейнер std::vector<uint16_t>
std::expected<std::vector<uint16_t>, ParseError> unpack_raw10_packet(std::span<const uint8_t> packet) {
    if (packet.size() < 6) {
        return std::unexpected(ParseError::BufferTooSmall);
    }

    std::span<const uint8_t, 4> raw_hdr(packet.data(), 4);
    auto header_res = parse_header(raw_hdr);
    if (!header_res) {
        return std::unexpected(header_res.error());
    }

    const auto& hdr = *header_res;
    if (hdr.data_type != DT_RAW10) {
        return std::unexpected(ParseError::InvalidDataType);
    }

    if (packet.size() < 4 + static_cast<size_t>(hdr.word_count) + 2) {
        return std::unexpected(ParseError::BufferTooSmall);
    }

    auto payload = packet.subspan(4, hdr.word_count);
    uint16_t rx_crc = static_cast<uint16_t>(packet[4 + hdr.word_count]) |
                      (static_cast<uint16_t>(packet[4 + hdr.word_count + 1]) << 8);

    if (rx_crc != calculate_crc16(payload)) {
        return std::unexpected(ParseError::CrcMismatch);
    }

    size_t num_blocks = hdr.word_count / 5;
    std::vector<uint16_t> pixels;
    pixels.reserve(num_blocks * 4);

    for (size_t i = 0; i < num_blocks; ++i) {
        const uint8_t* b = &payload[i * 5];
        uint8_t lsb = b[4];

        pixels.push_back(static_cast<uint16_t>((static_cast<uint16_t>(b[0]) << 2) | ((lsb >> 0) & 0x03)));
        pixels.push_back(static_cast<uint16_t>((static_cast<uint16_t>(b[1]) << 2) | ((lsb >> 2) & 0x03)));
        pixels.push_back(static_cast<uint16_t>((static_cast<uint16_t>(b[2]) << 2) | ((lsb >> 4) & 0x03)));
        pixels.push_back(static_cast<uint16_t>((static_cast<uint16_t>(b[3]) << 2) | ((lsb >> 6) & 0x03)));
    }

    return pixels;
}

} // namespace mipi::csi2
