// bgp_header_parser.cpp — Ідіоматичний парсер заголовка BGP на C++20
#include <iostream>
#include <array>
#include <span>
#include <expected>
#include <cstdint>
#include <algorithm>

enum class BgpMessageType : uint8_t {
    Open         = 1,
    Update       = 2,
    Notification = 3,
    Keepalive    = 4
};

enum class ParseError {
    BufferTooShort,
    InvalidMarker,
    InvalidLength
};

struct BgpHeader {
    std::array<uint8_t, 16> marker{};
    uint16_t length{0};
    BgpMessageType type{BgpMessageType::Keepalive};
};

class BgpParser {
public:
    static std::expected<BgpHeader, ParseError> parse_header(std::span<const uint8_t> bytes) noexcept {
        if (bytes.size() < 19) {
            return std::unexpected(ParseError::BufferTooShort);
        }

        BgpHeader hdr;
        std::copy_n(bytes.begin(), 16, hdr.marker.begin());

        // Перевірка маркера BGP (усі 16 байтів мають дорівнювати 0xFF)
        if (!std::all_of(hdr.marker.begin(), hdr.marker.end(), [](uint8_t b) { return b == 0xFF; })) {
            return std::unexpected(ParseError::InvalidMarker);
        }

        // Конвертація з мережевого порядку байтів (Big-Endian)
        hdr.length = static_cast<uint16_t>((bytes[16] << 8) | bytes[17]);
        hdr.type = static_cast<BgpMessageType>(bytes[18]);

        if (hdr.length < 19 || hdr.length > 4096) {
            return std::unexpected(ParseError::InvalidLength);
        }

        return hdr;
    }
};

int main() {
    const std::array<uint8_t, 19> raw_pkt = {
        0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
        0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
        0x00, 0x13, // Length: 19
        0x04        // Type: 4 (KEEPALIVE)
    };

    auto result = BgpParser::parse_header(raw_pkt);
    if (result) {
        std::cout << "[C++] BGP Packet Valid! Length: " << result->length
                  << ", Type: " << static_cast<int>(result->type) << "\n";
    } else {
        std::cout << "[C++] Header parsing failed!\n";
    }
    return 0;
}
