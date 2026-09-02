#include "frame.hpp"

namespace auth {
namespace {

// Little-Endian на дроті — не покладаємося на порядок байтів хоста.
void put_u16(std::byte* p, std::uint16_t v) noexcept {
    p[0] = static_cast<std::byte>(v & 0xFF);
    p[1] = static_cast<std::byte>(v >> 8);
}

void put_u32(std::byte* p, std::uint32_t v) noexcept {
    p[0] = static_cast<std::byte>(v & 0xFF);
    p[1] = static_cast<std::byte>((v >> 8) & 0xFF);
    p[2] = static_cast<std::byte>((v >> 16) & 0xFF);
    p[3] = static_cast<std::byte>((v >> 24) & 0xFF);
}

[[nodiscard]] std::uint16_t get_u16(const std::byte* p) noexcept {
    return static_cast<std::uint16_t>(std::to_integer<std::uint16_t>(p[0]) |
                                      (std::to_integer<std::uint16_t>(p[1]) << 8));
}

[[nodiscard]] std::uint32_t get_u32(const std::byte* p) noexcept {
    return std::to_integer<std::uint32_t>(p[0]) |
           (std::to_integer<std::uint32_t>(p[1]) << 8) |
           (std::to_integer<std::uint32_t>(p[2]) << 16) |
           (std::to_integer<std::uint32_t>(p[3]) << 24);
}

}  // namespace

std::uint16_t crc16_ccitt(std::span<const std::byte> data, std::uint16_t seed) noexcept {
    std::uint16_t crc = seed;
    for (const std::byte b : data) {
        crc ^= static_cast<std::uint16_t>(std::to_integer<std::uint16_t>(b) << 8);
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000) != 0 ? static_cast<std::uint16_t>((crc << 1) ^ 0x1021)
                                      : static_cast<std::uint16_t>(crc << 1);
        }
    }
    return crc;
}

std::vector<std::byte> encode(PacketHeader header, std::span<const std::byte> payload) {
    if (payload.size() > MaxPayload) {
        return {};  // навантаження арбітражу коротке; довше — помилка виклику
    }

    std::vector<std::byte> out(HeaderSize + payload.size());
    std::byte* p = out.data();

    p[0] = static_cast<std::byte>(MagicByte);
    p[1] = static_cast<std::byte>(ProtocolVersion);
    put_u16(p + 2, static_cast<std::uint16_t>(header.msg_id));
    p[4] = static_cast<std::byte>(header.source_id);
    p[5] = static_cast<std::byte>(header.target_id);
    put_u16(p + 6, header.seq_num);
    put_u32(p + 8, header.timestamp_ms);
    put_u32(p + 12, header.token_nonce);
    put_u16(p + 16, static_cast<std::uint16_t>(payload.size()));

    if (!payload.empty()) {
        std::memcpy(p + HeaderSize, payload.data(), payload.size());
    }

    // CRC накриває вісімнадцять байтів заголовка (усе, крім самого поля
    // CRC) і все корисне навантаження.
    std::uint16_t crc = crc16_ccitt(std::span{out}.first(18));
    crc = crc16_ccitt(std::span{out}.subspan(HeaderSize), crc);
    put_u16(p + 18, crc);

    return out;
}

std::expected<Frame, StatusCode> decode(std::span<const std::byte> raw) noexcept {
    if (raw.size() < HeaderSize) {
        return std::unexpected(StatusCode::BadLength);
    }
    if (std::to_integer<std::uint8_t>(raw[0]) != MagicByte) {
        return std::unexpected(StatusCode::BadMagic);
    }
    if (std::to_integer<std::uint8_t>(raw[1]) != ProtocolVersion) {
        return std::unexpected(StatusCode::BadVersion);
    }

    const std::uint16_t plen = get_u16(raw.data() + 16);
    if (plen > MaxPayload || HeaderSize + plen > raw.size()) {
        return std::unexpected(StatusCode::BadLength);
    }

    std::uint16_t crc = crc16_ccitt(raw.first(18));
    crc = crc16_ccitt(raw.subspan(HeaderSize, plen), crc);
    if (crc != get_u16(raw.data() + 18)) {
        return std::unexpected(StatusCode::CrcMismatch);
    }

    Frame frame{};
    frame.header.magic        = std::to_integer<std::uint8_t>(raw[0]);
    frame.header.version      = std::to_integer<std::uint8_t>(raw[1]);
    frame.header.msg_id       = static_cast<MessageId>(get_u16(raw.data() + 2));
    frame.header.source_id    = std::to_integer<std::uint8_t>(raw[4]);
    frame.header.target_id    = std::to_integer<std::uint8_t>(raw[5]);
    frame.header.seq_num      = get_u16(raw.data() + 6);
    frame.header.timestamp_ms = get_u32(raw.data() + 8);
    frame.header.token_nonce  = get_u32(raw.data() + 12);
    frame.header.payload_len  = plen;
    frame.header.crc16        = get_u16(raw.data() + 18);
    frame.payload             = raw.subspan(HeaderSize, plen);
    return frame;
}

std::optional<std::size_t> find_start(std::span<const std::byte> raw) noexcept {
    for (std::size_t i = 0; i < raw.size(); ++i) {
        if (std::to_integer<std::uint8_t>(raw[i]) != MagicByte) {
            continue;
        }
        // Другий байт уже видно — відкидаємо випадкове 0xAA всередині даних.
        if (i + 1 < raw.size() &&
            std::to_integer<std::uint8_t>(raw[i + 1]) != ProtocolVersion) {
            continue;
        }
        return i;
    }
    return std::nullopt;
}

std::uint32_t sign_override(std::uint32_t key, std::uint8_t src, std::uint16_t seq,
                            std::uint32_t ts) noexcept {
    std::byte buf[11]{};
    put_u32(buf, key);
    buf[4] = static_cast<std::byte>(src);
    put_u16(buf + 5, seq);
    put_u32(buf + 7, ts);

    // FNV-1a: дешево й детерміновано з обох боків каналу.
    std::uint32_t hash = 2166136261u;
    for (const std::byte b : buf) {
        hash ^= std::to_integer<std::uint32_t>(b);
        hash *= 16777619u;
    }
    return hash;
}

}  // namespace auth
