#include "protocol.hpp"

#include <algorithm>

namespace field {
namespace {

// Дрібний писар: кладе поля підряд у little-endian. Порядок байтів тут
// видно очима, тому кадр не залежить від архітектури хоста.
class Writer {
public:
    explicit Writer(Wire& out) noexcept : out_(out) {}

    void u8(std::uint8_t v) noexcept { out_[pos_++] = std::byte{v}; }
    void u16(std::uint16_t v) noexcept {
        u8(static_cast<std::uint8_t>(v & 0xFF));
        u8(static_cast<std::uint8_t>((v >> 8) & 0xFF));
    }
    void u32(std::uint32_t v) noexcept {
        u16(static_cast<std::uint16_t>(v & 0xFFFF));
        u16(static_cast<std::uint16_t>((v >> 16) & 0xFFFF));
    }
    void i16(std::int16_t v) noexcept { u16(static_cast<std::uint16_t>(v)); }
    void pad(std::size_t n) noexcept { for (std::size_t i = 0; i < n; ++i) u8(0); }

private:
    Wire& out_;
    std::size_t pos_{0};
};

class Reader {
public:
    explicit Reader(WireView in) noexcept : in_(in) {}

    [[nodiscard]] std::uint8_t u8() noexcept { return std::to_integer<std::uint8_t>(in_[pos_++]); }
    [[nodiscard]] std::uint16_t u16() noexcept {
        const auto lo = static_cast<std::uint16_t>(u8());
        const auto hi = static_cast<std::uint16_t>(u8());
        return static_cast<std::uint16_t>(lo | (hi << 8));
    }
    [[nodiscard]] std::uint32_t u32() noexcept {
        const auto lo = static_cast<std::uint32_t>(u16());
        const auto hi = static_cast<std::uint32_t>(u16());
        return lo | (hi << 16);
    }
    [[nodiscard]] std::int16_t i16() noexcept { return static_cast<std::int16_t>(u16()); }
    void skip(std::size_t n) noexcept { pos_ += n; }

private:
    WireView in_;
    std::size_t pos_{0};
};

// Дописує CRC у два останні байти вже зібраного кадру.
void seal(Wire& wire) noexcept {
    const auto body = std::span<const std::byte>(wire).first(kFrameSize - 2);
    const std::uint16_t crc = crc16_ccitt(body);
    wire[kFrameSize - 2] = std::byte{static_cast<std::uint8_t>(crc & 0xFF)};
    wire[kFrameSize - 1] = std::byte{static_cast<std::uint8_t>((crc >> 8) & 0xFF)};
}

// Спільна для всіх трьох типів шапка: магія, тип, адреса вузла, номер.
void head(Writer& w, FrameType type, std::uint16_t node_id, std::uint32_t seq) noexcept {
    w.u8(kMagic);
    w.u8(static_cast<std::uint8_t>(type));
    w.u16(node_id);
    w.u32(seq);
}

}  // namespace

std::string_view describe(DecodeError err) noexcept {
    switch (err) {
        case DecodeError::BadMagic:    return "немає синхробайта 0xAA";
        case DecodeError::BadCrc:      return "CRC-16 не зійшлася";
        case DecodeError::UnknownType: return "невідомий тип кадру";
    }
    return "невідома помилка";
}

std::uint16_t crc16_ccitt(std::span<const std::byte> data) noexcept {
    std::uint16_t crc = 0xFFFF;
    for (std::byte b : data) {
        crc ^= static_cast<std::uint16_t>(std::to_integer<std::uint8_t>(b) << 8);
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000) ? static_cast<std::uint16_t>((crc << 1) ^ 0x1021)
                                 : static_cast<std::uint16_t>(crc << 1);
        }
    }
    return crc;
}

Wire encode(const Telemetry& t) noexcept {
    Wire wire{};
    Writer w{wire};
    head(w, FrameType::Telemetry, t.node_id, t.seq);
    w.i16(t.temp_c100);
    w.u16(t.battery_mv);
    w.u8(t.flags.bits());
    w.pad(1);
    seal(wire);
    return wire;
}

Wire encode(const Command& c) noexcept {
    Wire wire{};
    Writer w{wire};
    head(w, FrameType::Command, c.node_id, c.seq);
    w.u8(static_cast<std::uint8_t>(c.id));
    w.u8(c.value);
    w.pad(4);
    seal(wire);
    return wire;
}

Wire encode(const Ack& a) noexcept {
    Wire wire{};
    Writer w{wire};
    head(w, FrameType::Ack, a.node_id, a.seq);
    w.u8(a.cmd_id);
    w.u8(static_cast<std::uint8_t>(a.status));
    w.u8(a.flags.bits());
    w.pad(3);
    seal(wire);
    return wire;
}

bool looks_valid(WireView wire) noexcept {
    if (std::to_integer<std::uint8_t>(wire[0]) != kMagic) {
        return false;
    }
    const auto rx = static_cast<std::uint16_t>(
        std::to_integer<std::uint8_t>(wire[kFrameSize - 2]) |
        (std::to_integer<std::uint8_t>(wire[kFrameSize - 1]) << 8));
    return rx == crc16_ccitt(wire.first(kFrameSize - 2));
}

std::expected<Frame, DecodeError> decode(WireView wire) noexcept {
    if (std::to_integer<std::uint8_t>(wire[0]) != kMagic) {
        return std::unexpected(DecodeError::BadMagic);
    }
    if (!looks_valid(wire)) {
        return std::unexpected(DecodeError::BadCrc);
    }

    Reader r{wire};
    (void)r.u8();                       // магія вже перевірена
    const auto type = static_cast<FrameType>(r.u8());
    const auto node_id = r.u16();
    const auto seq = r.u32();

    switch (type) {
        case FrameType::Telemetry: {
            Telemetry t{};
            t.node_id = node_id;
            t.seq = seq;
            t.temp_c100 = r.i16();
            t.battery_mv = r.u16();
            t.flags = Flags::from_bits(r.u8());
            return Frame{t};
        }
        case FrameType::Command: {
            Command c{};
            c.node_id = node_id;
            c.seq = seq;
            c.id = static_cast<CommandId>(r.u8());
            c.value = r.u8();
            return Frame{c};
        }
        case FrameType::Ack: {
            Ack a{};
            a.node_id = node_id;
            a.seq = seq;
            a.cmd_id = r.u8();
            a.status = static_cast<AckStatus>(r.u8());
            a.flags = Flags::from_bits(r.u8());
            return Frame{a};
        }
    }
    return std::unexpected(DecodeError::UnknownType);
}

void StreamFramer::drop_front(std::size_t count) {
    buf_.erase(buf_.begin(), buf_.begin() + static_cast<std::ptrdiff_t>(count));
}

void StreamFramer::feed(std::span<const std::byte> chunk) {
    buf_.insert(buf_.end(), chunk.begin(), chunk.end());

    // Стеля буфера: якщо в потоці саме́ сміття, воно не має рости без меж.
    if (buf_.size() > kCapacity) {
        const std::size_t excess = buf_.size() - kCapacity;
        drops_ += excess;
        drop_front(excess);
    }
}

std::optional<Wire> StreamFramer::next() {
    for (;;) {
        const auto magic_at = std::find(buf_.begin(), buf_.end(), std::byte{kMagic});
        if (const auto garbage = static_cast<std::size_t>(magic_at - buf_.begin()); garbage > 0) {
            drops_ += garbage;
            drop_front(garbage);
        }
        if (buf_.size() < kFrameSize) {
            return std::nullopt;   // кадр іще не добрався цілком
        }

        Wire candidate{};
        std::copy_n(buf_.begin(), kFrameSize, candidate.begin());
        if (looks_valid(candidate)) {
            drop_front(kFrameSize);
            return candidate;
        }

        // 0xAA всередині даних побитого кадру: крок на один байт уперед.
        ++drops_;
        drop_front(1);
    }
}

}  // namespace field
