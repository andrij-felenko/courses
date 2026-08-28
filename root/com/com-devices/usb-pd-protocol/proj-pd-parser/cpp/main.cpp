#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>
#include <expected>

namespace usb_pd {

enum class MessageType : uint8_t {
    GoodCRC       = 0x01,
    GotoMin       = 0x02,
    Accept        = 0x03,
    Reject        = 0x04,
    Ping          = 0x05,
    PsRdy         = 0x06,
    GetSourceCap  = 0x07,
    GetSinkCap    = 0x08,
    DrSwap        = 0x09,
    PrSwap        = 0x0A,
    VconnSwap     = 0x0B,
    Wait          = 0x0C,
    SoftReset     = 0x0D,
    NotSupported  = 0x10,

    SourceCap     = 0x01,
    Request       = 0x02,
    Bist          = 0x03,
    SinkCap       = 0x04,
    Vdm           = 0x0F
};

enum class PowerRole : uint8_t { Sink = 0, Source = 1 };
enum class DataRole  : uint8_t { Ufp = 0, Dfp = 1 };
enum class SpecRev   : uint8_t { Rev1_0 = 0, Rev2_0 = 1, Rev3_0 = 2 };

enum class ParseError {
    BufferTooShort,
    CrcMismatch,
    InvalidPayloadLength,
    InvalidExtendedHeader
};

struct Header {
    bool is_extended;
    uint8_t num_data_objects;
    uint8_t message_id;
    PowerRole power_role;
    SpecRev spec_rev;
    DataRole data_role;
    MessageType msg_type;

    static constexpr Header from_raw(uint16_t raw) noexcept {
        return Header{
            .is_extended = static_cast<bool>((raw >> 15) & 0x01),
            .num_data_objects = static_cast<uint8_t>((raw >> 12) & 0x07),
            .message_id = static_cast<uint8_t>((raw >> 9) & 0x07),
            .power_role = static_cast<PowerRole>((raw >> 8) & 0x01),
            .spec_rev = static_cast<SpecRev>((raw >> 6) & 0x03),
            .data_role = static_cast<DataRole>((raw >> 5) & 0x01),
            .msg_type = static_cast<MessageType>(raw & 0x1F)
        };
    }

    constexpr uint16_t to_raw() const noexcept {
        uint16_t raw = static_cast<uint8_t>(msg_type) & 0x1F;
        raw |= (static_cast<uint16_t>(data_role) & 0x01) << 5;
        raw |= (static_cast<uint16_t>(spec_rev) & 0x03) << 6;
        raw |= (static_cast<uint16_t>(power_role) & 0x01) << 8;
        raw |= (static_cast<uint16_t>(message_id) & 0x07) << 9;
        raw |= (static_cast<uint16_t>(num_data_objects) & 0x07) << 12;
        raw |= (static_cast<uint16_t>(is_extended) & 0x01) << 15;
        return raw;
    }
};

struct ExtendedHeader {
    bool chunked;
    uint8_t chunk_number;
    bool request_chunk;
    uint16_t data_size;

    static constexpr ExtendedHeader from_raw(uint16_t raw) noexcept {
        return ExtendedHeader{
            .chunked = static_cast<bool>((raw >> 15) & 0x01),
            .chunk_number = static_cast<uint8_t>((raw >> 11) & 0x0F),
            .request_chunk = static_cast<bool>((raw >> 10) & 0x01),
            .data_size = static_cast<uint16_t>(raw & 0x01FF)
        };
    }
};

struct Packet {
    Header header;
    std::optional<ExtendedHeader> ext_header;
    std::span<const uint8_t> payload;
};

// Розрахунок CRC-32 (нібловий метод)
constexpr uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
    constexpr std::array<uint32_t, 16> table = {
        0x00000000, 0x1DB71064, 0x3B6E20C8, 0x26D930AC,
        0x76DC4190, 0x6B6B51F4, 0x4DB26158, 0x5005713C,
        0xEDB88320, 0xF00F9344, 0xD6D6A3E8, 0xCB61B38C,
        0x9B64C2B0, 0x86D3D2D4, 0xA00AE278, 0xBDBDF21C
    };
    uint32_t crc = 0xFFFFFFFFu;
    for (uint8_t b : data) {
        crc ^= b;
        crc = (crc >> 4) ^ table[crc & 0x0F];
        crc = (crc >> 4) ^ table[(crc ^ (b >> 4)) & 0x0F];
    }
    return ~crc;
}

// Парсер кадру пакета
std::expected<Packet, ParseError> parse_packet(std::span<const uint8_t> raw_frame) noexcept {
    if (raw_frame.size() < 6) {
        return std::unexpected(ParseError::BufferTooShort);
    }

    const size_t content_len = raw_frame.size() - 4;
    const uint32_t expected_crc = calculate_crc32(raw_frame.subspan(0, content_len));

    const uint32_t packet_crc = static_cast<uint32_t>(raw_frame[content_len]) |
                                (static_cast<uint32_t>(raw_frame[content_len + 1]) << 8) |
                                (static_cast<uint32_t>(raw_frame[content_len + 2]) << 16) |
                                (static_cast<uint32_t>(raw_frame[content_len + 3]) << 24);

    if (expected_crc != packet_crc) {
        return std::unexpected(ParseError::CrcMismatch);
    }

    const uint16_t raw_hdr = static_cast<uint16_t>(raw_frame[0]) |
                             (static_cast<uint16_t>(raw_frame[1]) << 8);
    const Header hdr = Header::from_raw(raw_hdr);

    if (!hdr.is_extended) {
        const size_t expected_payload_bytes = static_cast<size_t>(hdr.num_data_objects) * 4;
        if (content_len != 2 + expected_payload_bytes) {
            return std::unexpected(ParseError::InvalidPayloadLength);
        }
        return Packet{
            .header = hdr,
            .ext_header = std::nullopt,
            .payload = raw_frame.subspan(2, expected_payload_bytes)
        };
    } else {
        if (content_len < 4) {
            return std::unexpected(ParseError::InvalidExtendedHeader);
        }
        const uint16_t raw_ext = static_cast<uint16_t>(raw_frame[2]) |
                                 (static_cast<uint16_t>(raw_frame[3]) << 8);
        return Packet{
            .header = hdr,
            .ext_header = ExtendedHeader::from_raw(raw_ext),
            .payload = raw_frame.subspan(4, content_len - 4)
        };
    }
}

// Генерація кадру GoodCRC (повертає фіксований масив із 6 байтів)
constexpr std::array<uint8_t, 6> make_goodcrc(uint8_t msg_id, PowerRole role,
                                              DataRole data_role, SpecRev rev) noexcept {
    const Header hdr{
        .is_extended = false,
        .num_data_objects = 0,
        .message_id = msg_id,
        .power_role = role,
        .spec_rev = rev,
        .data_role = data_role,
        .msg_type = MessageType::GoodCRC
    };
    const uint16_t raw_hdr = hdr.to_raw();
    std::array<uint8_t, 6> buf = {
        static_cast<uint8_t>(raw_hdr & 0xFF),
        static_cast<uint8_t>((raw_hdr >> 8) & 0xFF),
        0, 0, 0, 0
    };
    const uint32_t crc = calculate_crc32(std::span<const uint8_t>(buf.data(), 2));
    buf[2] = static_cast<uint8_t>(crc & 0xFF);
    buf[3] = static_cast<uint8_t>((crc >> 8) & 0xFF);
    buf[4] = static_cast<uint8_t>((crc >> 16) & 0xFF);
    buf[5] = static_cast<uint8_t>((crc >> 24) & 0xFF);
    return buf;
}

} // namespace usb_pd
