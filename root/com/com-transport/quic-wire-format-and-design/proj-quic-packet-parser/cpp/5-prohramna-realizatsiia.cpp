#include <iostream>
#include <span>
#include <string_view>
#include <vector>
#include <optional>
#include <expected>
#include <cstdint>
#include <cstring>

namespace quic {

inline constexpr size_t kMaxCidLen = 20;
inline constexpr uint32_t kQuicVersion1 = 0x00000001;

enum class Error {
    BufferTooShort,
    InvalidVarint,
    InvalidVersion,
    CidTooLong,
    UnknownFrame
};

enum class PacketType {
    Initial   = 0x00,
    ZeroRtt   = 0x01,
    Handshake = 0x02,
    Retry     = 0x03,
    OneRttShort
};

struct ConnectionId {
    uint8_t len{0};
    uint8_t data[kMaxCidLen]{0};

    [[nodiscard]] std::span<const uint8_t> as_span() const noexcept {
        return {data, len};
    }
};

struct PacketHeader {
    PacketType type{PacketType::Initial};
    bool is_long_header{true};
    uint32_t version{0};
    ConnectionId dcid;
    ConnectionId scid;
    std::span<const uint8_t> token;
    std::span<const uint8_t> payload;
};

struct StreamFrame {
    uint64_t stream_id{0};
    uint64_t offset{0};
    bool fin{false};
    std::span<const uint8_t> data;
};

struct AckFrame {
    uint64_t largest_acked{0};
    uint64_t ack_delay{0};
    uint64_t first_ack_range{0};
    uint64_t range_count{0};
};

/* Декодування цілого числа змінної довжини (RFC 9000 §16) */
[[nodiscard]] inline std::expected<uint64_t, Error> read_varint(std::span<const uint8_t>& buf) noexcept {
    if (buf.empty()) {
        return std::unexpected(Error::BufferTooShort);
    }

    const uint8_t first = buf[0];
    const uint8_t prefix = (first >> 6) & 0x03;
    const size_t len = static_cast<size_t>(1) << prefix;

    if (buf.size() < len) {
        return std::unexpected(Error::BufferTooShort);
    }

    uint64_t res = first & 0x3F;
    buf = buf.subspan(1);

    for (size_t i = 1; i < len; ++i) {
        res = (res << 8) | buf[0];
        buf = buf.subspan(1);
    }

    return res;
}

/* Безпечний розбір бінарного заголовка пакета QUIC */
[[nodiscard]] inline std::expected<PacketHeader, Error> parse_header(
    std::span<const uint8_t> raw, size_t dcid_len_for_short) noexcept {
    if (raw.empty()) {
        return std::unexpected(Error::BufferTooShort);
    }

    PacketHeader hdr;
    const uint8_t first_byte = raw[0];
    raw = raw.subspan(1);

    hdr.is_long_header = (first_byte & 0x80) != 0;

    if (hdr.is_long_header) {
        if (raw.size() < 4) return std::unexpected(Error::BufferTooShort);
        hdr.version = (static_cast<uint32_t>(raw[0]) << 24) |
                      (static_cast<uint32_t>(raw[1]) << 16) |
                      (static_cast<uint32_t>(raw[2]) << 8)  |
                      (static_cast<uint32_t>(raw[3]));
        raw = raw.subspan(4);

        const uint8_t type_bits = (first_byte >> 4) & 0x03;
        hdr.type = static_cast<PacketType>(type_bits);

        /* DCID */
        if (raw.empty()) return std::unexpected(Error::BufferTooShort);
        const uint8_t dcil = raw[0];
        raw = raw.subspan(1);
        if (dcil > kMaxCidLen) return std::unexpected(Error::CidTooLong);
        if (raw.size() < dcil) return std::unexpected(Error::BufferTooShort);
        hdr.dcid.len = dcil;
        std::memcpy(hdr.dcid.data, raw.data(), dcil);
        raw = raw.subspan(dcil);

        /* SCID */
        if (raw.empty()) return std::unexpected(Error::BufferTooShort);
        const uint8_t scil = raw[0];
        raw = raw.subspan(1);
        if (scil > kMaxCidLen) return std::unexpected(Error::CidTooLong);
        if (raw.size() < scil) return std::unexpected(Error::BufferTooShort);
        hdr.scid.len = scil;
        std::memcpy(hdr.scid.data, raw.data(), scil);
        raw = raw.subspan(scil);

        /* Token for Initial */
        if (hdr.type == PacketType::Initial) {
            auto token_len = read_varint(raw);
            if (!token_len) return std::unexpected(token_len.error());
            if (raw.size() < *token_len) return std::unexpected(Error::BufferTooShort);
            hdr.token = raw.first(static_cast<size_t>(*token_len));
            raw = raw.subspan(static_cast<size_t>(*token_len));
        }

        /* Payload length */
        auto payload_len = read_varint(raw);
        if (!payload_len) return std::unexpected(payload_len.error());
        if (raw.size() < *payload_len) return std::unexpected(Error::BufferTooShort);

        hdr.payload = raw.first(static_cast<size_t>(*payload_len));
    } else {
        /* Short Header */
        hdr.type = PacketType::OneRttShort;
        hdr.version = 0;

        if (dcid_len_for_short > kMaxCidLen) return std::unexpected(Error::CidTooLong);
        if (raw.size() < dcid_len_for_short) return std::unexpected(Error::BufferTooShort);

        hdr.dcid.len = static_cast<uint8_t>(dcid_len_for_short);
        std::memcpy(hdr.dcid.data, raw.data(), dcid_len_for_short);
        raw = raw.subspan(dcid_len_for_short);

        hdr.payload = raw;
    }

    return hdr;
}

/* Розбір кадру STREAM з розшифрованого корисного навантаження */
[[nodiscard]] inline std::expected<StreamFrame, Error> parse_stream_frame(
    std::span<const uint8_t> payload) noexcept {
    if (payload.empty()) {
        return std::unexpected(Error::BufferTooShort);
    }

    const uint8_t ftype = payload[0];
    payload = payload.subspan(1);

    if (ftype < 0x08 || ftype > 0x0F) {
        return std::unexpected(Error::UnknownFrame);
    }

    const bool has_off = (ftype & 0x04) != 0;
    const bool has_len = (ftype & 0x02) != 0;

    StreamFrame frame;
    frame.fin = (ftype & 0x01) != 0;

    auto stream_id = read_varint(payload);
    if (!stream_id) return std::unexpected(stream_id.error());
    frame.stream_id = *stream_id;

    if (has_off) {
        auto offset = read_varint(payload);
        if (!offset) return std::unexpected(offset.error());
        frame.offset = *offset;
    } else {
        frame.offset = 0;
    }

    if (has_len) {
        auto len = read_varint(payload);
        if (!len) return std::unexpected(len.error());
        if (payload.size() < *len) return std::unexpected(Error::BufferTooShort);
        frame.data = payload.first(static_cast<size_t>(*len));
    } else {
        frame.data = payload;
    }

    return frame;
}

/* Розбір кадру ACK */
[[nodiscard]] inline std::expected<AckFrame, Error> parse_ack_frame(
    std::span<const uint8_t> payload) noexcept {
    if (payload.empty()) {
        return std::unexpected(Error::BufferTooShort);
    }

    const uint8_t ftype = payload[0];
    payload = payload.subspan(1);

    if (ftype != 0x02 && ftype != 0x03) {
        return std::unexpected(Error::UnknownFrame);
    }

    AckFrame ack;
    auto largest = read_varint(payload);
    if (!largest) return std::unexpected(largest.error());
    ack.largest_acked = *largest;

    auto delay = read_varint(payload);
    if (!delay) return std::unexpected(delay.error());
    ack.ack_delay = *delay;

    auto count = read_varint(payload);
    if (!count) return std::unexpected(count.error());
    ack.range_count = *count;

    auto first_range = read_varint(payload);
    if (!first_range) return std::unexpected(first_range.error());
    ack.first_ack_range = *first_range;

    return ack;
}

} // namespace quic
