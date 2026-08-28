#include <iostream>
#include <iomanip>
#include <span>
#include <string_view>
#include <optional>
#include <vector>
#include <cstdint>

namespace osi {

enum class NetworkProtocolId : uint8_t {
    InactiveSubnetwork = 0x00,
    CLNP               = 0x81,
    ESIS               = 0x82,
    ISIS               = 0x83
};

enum class Tp4Type : uint8_t {
    DataAck           = 0x70,
    DisconnectRequest = 0x80,
    ConnectionConfirm = 0xD0,
    ConnectionRequest = 0xE0,
    Data              = 0xF0
};

struct NsapAddress {
    std::span<const uint8_t> raw_bytes;

    void print() const {
        for (size_t i = 0; i < raw_bytes.size(); ++i) {
            std::cout << std::hex << std::uppercase << std::setw(2) << std::setfill('0')
                      << static_cast<int>(raw_bytes[i]);
            if (i % 2 == 1 && i != raw_bytes.size() - 1) {
                std::cout << ".";
            }
        }
        std::cout << std::dec;
    }
};

struct ClnpHeader {
    uint8_t nlpid{0};
    uint8_t header_len{0};
    uint8_t version{0};
    uint8_t lifetime{0};
    uint8_t flags{0};
    uint16_t segment_len{0};
    uint16_t checksum{0};
    bool is_segmented{false};
    bool more_segments{false};
    bool error_report{false};
    uint8_t type{0};

    NsapAddress dst_nsap;
    NsapAddress src_nsap;

    uint16_t duid{0};
    uint16_t segment_offset{0};
    uint16_t total_len{0};

    std::span<const uint8_t> payload;
};

struct Tp4DtHeader {
    uint8_t header_len{0};
    Tp4Type type{Tp4Type::Data};
    uint16_t dst_ref{0};
    uint8_t tpdu_nr{0};
    bool eot{false};
    std::span<const uint8_t> payload;
};

class PacketParser {
public:
    static bool verifyFletcher16(std::span<const uint8_t> header) noexcept {
        if (header.empty()) return false;
        if (header.size() >= 9 && header[7] == 0x00 && header[8] == 0x00) {
            return true; /* Перевірку вимкнено */
        }

        uint32_t c0 = 0;
        uint32_t c1 = 0;

        for (uint8_t byte : header) {
            c0 += byte;
            c1 += c0;
        }

        return ((c0 % 255) == 0) && ((c1 % 255) == 0);
    }

    static std::optional<ClnpHeader> parseClnp(std::span<const uint8_t> buffer) noexcept {
        if (buffer.size() < 9) return std::nullopt;

        ClnpHeader hdr;
        hdr.nlpid = buffer[0];
        if (hdr.nlpid != static_cast<uint8_t>(NetworkProtocolId::CLNP)) {
            return std::nullopt;
        }

        hdr.header_len = buffer[1];
        if (hdr.header_len < 9 || hdr.header_len > buffer.size()) {
            return std::nullopt;
        }

        hdr.version = buffer[2];
        hdr.lifetime = buffer[3];
        hdr.flags = buffer[4];
        hdr.type = hdr.flags & 0x1F;
        hdr.is_segmented = (hdr.flags & 0x80) != 0;
        hdr.more_segments = (hdr.flags & 0x40) != 0;
        hdr.error_report = (hdr.flags & 0x20) != 0;

        hdr.segment_len = (static_cast<uint16_t>(buffer[5]) << 8) | buffer[6];
        hdr.checksum = (static_cast<uint16_t>(buffer[7]) << 8) | buffer[8];

        /* Перевірка суми Флетчера */
        if (!verifyFletcher16(buffer.subspan(0, hdr.header_len))) {
            return std::nullopt;
        }

        size_t offset = 9;

        /* Розбір адреси призначення NSAP */
        if (offset >= hdr.header_len) return std::nullopt;
        uint8_t dst_len = buffer[offset++];
        if (dst_len > 20 || offset + dst_len > hdr.header_len) return std::nullopt;
        hdr.dst_nsap = NsapAddress{buffer.subspan(offset, dst_len)};
        offset += dst_len;

        /* Розбір адреси джерела NSAP */
        if (offset >= hdr.header_len) return std::nullopt;
        uint8_t src_len = buffer[offset++];
        if (src_len > 20 || offset + src_len > hdr.header_len) return std::nullopt;
        hdr.src_nsap = NsapAddress{buffer.subspan(offset, src_len)};
        offset += src_len;

        /* Частина сегментації */
        if (hdr.is_segmented) {
            if (offset + 6 > hdr.header_len) return std::nullopt;
            hdr.duid = (static_cast<uint16_t>(buffer[offset]) << 8) | buffer[offset + 1];
            hdr.segment_offset = (static_cast<uint16_t>(buffer[offset + 2]) << 8) | buffer[offset + 3];
            hdr.total_len = (static_cast<uint16_t>(buffer[offset + 4]) << 8) | buffer[offset + 5];
            offset += 6;
        }

        size_t payload_len = (hdr.segment_len >= hdr.header_len && hdr.segment_len <= buffer.size())
                           ? (hdr.segment_len - hdr.header_len)
                           : (buffer.size() - hdr.header_len);

        hdr.payload = buffer.subspan(hdr.header_len, payload_len);
        return hdr;
    }

    static std::optional<Tp4DtHeader> parseTp4Dt(std::span<const uint8_t> buffer) noexcept {
        if (buffer.size() < 5) return std::nullopt;

        Tp4DtHeader tp;
        tp.header_len = buffer[0];
        if (tp.header_len < 4 || (static_cast<size_t>(tp.header_len) + 1) > buffer.size()) {
            return std::nullopt;
        }

        uint8_t type_raw = buffer[1] & 0xF0;
        if (type_raw != static_cast<uint8_t>(Tp4Type::Data)) {
            return std::nullopt;
        }
        tp.type = Tp4Type::Data;

        tp.dst_ref = (static_cast<uint16_t>(buffer[2]) << 8) | buffer[3];
        tp.eot = (buffer[4] & 0x80) != 0;
        tp.tpdu_nr = buffer[4] & 0x7F;

        size_t total_hdr = static_cast<size_t>(tp.header_len) + 1;
        tp.payload = buffer.subspan(total_hdr);
        return tp;
    }
};

} // namespace osi
