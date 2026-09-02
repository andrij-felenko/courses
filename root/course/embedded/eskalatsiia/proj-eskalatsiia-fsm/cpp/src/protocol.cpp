#include "escalation/protocol.hpp"

#include <bit>

namespace esc {
namespace {

// magic(1) ver(1) flags(1) query_id(2) timestamp(4) deadline(2) trigger(1)
// position(12) velocity(12) options_count(1)
constexpr std::size_t kQueryFixed = 37;
constexpr std::size_t kReplyLen   = 11;

class Writer {
public:
    explicit Writer(std::span<std::byte> out) noexcept : out_{out} {}

    void u8(std::uint8_t v) noexcept {
        if (!ok_) return;
        if (n_ >= out_.size()) { ok_ = false; return; }
        out_[n_++] = std::byte{v};
    }
    void u16(std::uint16_t v) noexcept {
        u8(static_cast<std::uint8_t>(v & 0xFF));
        u8(static_cast<std::uint8_t>(v >> 8));
    }
    void u32(std::uint32_t v) noexcept {
        u16(static_cast<std::uint16_t>(v & 0xFFFF));
        u16(static_cast<std::uint16_t>(v >> 16));
    }
    void f32(float v) noexcept { u32(std::bit_cast<std::uint32_t>(v)); }
    void bytes(std::span<const std::byte> src) noexcept {
        for (auto b : src) u8(std::to_integer<std::uint8_t>(b));
    }
    void chars(std::string_view s) noexcept {
        for (char c : s) u8(static_cast<std::uint8_t>(c));
    }

    [[nodiscard]] bool ok() const noexcept { return ok_; }
    [[nodiscard]] std::size_t size() const noexcept { return n_; }
    [[nodiscard]] std::span<const std::byte> written() const noexcept { return out_.first(n_); }

private:
    std::span<std::byte> out_;
    std::size_t          n_{0};
    bool                 ok_{true};
};

class Reader {
public:
    explicit Reader(std::span<const std::byte> in, std::size_t start = 0) noexcept
        : in_{in}, n_{start} {}

    std::uint8_t u8() noexcept {
        if (!ok_) return 0;
        if (n_ >= in_.size()) { ok_ = false; return 0; }
        return std::to_integer<std::uint8_t>(in_[n_++]);
    }
    std::uint16_t u16() noexcept {
        const std::uint16_t lo = u8();
        const std::uint16_t hi = u8();
        return static_cast<std::uint16_t>(lo | (hi << 8));
    }
    std::uint32_t u32() noexcept {
        const std::uint32_t lo = u16();
        const std::uint32_t hi = u16();
        return lo | (hi << 16);
    }
    float f32() noexcept { return std::bit_cast<float>(u32()); }

    std::span<const std::byte> take(std::size_t len) noexcept {
        if (!ok_ || n_ + len > in_.size()) { ok_ = false; return {}; }
        const auto s = in_.subspan(n_, len);
        n_ += len;
        return s;
    }
    std::string_view take_chars(std::size_t len) noexcept {
        const auto s = take(len);
        if (s.empty() && len > 0) return {};
        return std::string_view{reinterpret_cast<const char*>(s.data()), s.size()};
    }

    [[nodiscard]] bool ok() const noexcept { return ok_; }

private:
    std::span<const std::byte> in_;
    std::size_t                n_{0};
    bool                       ok_{true};
};

[[nodiscard]] std::size_t query_size(const Query& q, bool with_roi) noexcept {
    std::size_t n = kQueryFixed;
    for (const auto& o : q.options) {
        n += 2 + std::min(o.description.size(), kDescMax) + 8;
    }
    n += 2;                       // довжина ROI
    if (with_roi) n += q.roi.size();
    n += 2;                       // CRC
    return n;
}

}  // namespace

std::uint16_t crc16(std::span<const std::byte> data) noexcept {
    // CRC-16/CCITT-FALSE: поліном 0x1021, початкове 0xFFFF
    std::uint16_t crc = 0xFFFF;
    for (auto b : data) {
        crc ^= static_cast<std::uint16_t>(std::to_integer<std::uint16_t>(b) << 8);
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000) ? static_cast<std::uint16_t>((crc << 1) ^ 0x1021)
                                 : static_cast<std::uint16_t>(crc << 1);
        }
    }
    return crc;
}

std::expected<std::span<const std::byte>, WireError>
pack_query(const Query& q, std::span<std::byte> out) noexcept {
    if (q.options.empty() || q.options.size() > kMaxOptions) {
        return std::unexpected{WireError::Field};
    }
    if (q.roi.size() > kRoiMax) {
        return std::unexpected{WireError::Field};
    }

    const std::size_t limit = std::min(out.size(), kMtuBytes);

    // Мініатюру ріжемо цілком, а не наполовину: обрізаний JPEG декодеру не потрібен
    std::uint8_t flags    = q.flags;
    bool         with_roi = true;
    if (query_size(q, true) > limit) {
        with_roi = false;
        flags   |= kFlagRoiDropped;
        if (query_size(q, false) > limit) {
            return std::unexpected{WireError::NoRoom};
        }
    }

    Writer w{out.first(limit)};
    w.u8(std::to_integer<std::uint8_t>(kMagicQuery));
    w.u8(std::to_integer<std::uint8_t>(kWireVersion));
    w.u8(flags);
    w.u16(q.query_id);
    w.u32(static_cast<std::uint32_t>(q.timestamp.count()));
    w.u16(static_cast<std::uint16_t>(std::min<std::int64_t>(q.deadline.count(), 65535)));
    w.u8(static_cast<std::uint8_t>(q.trigger));
    for (float v : q.position) w.f32(v);
    for (float v : q.velocity) w.f32(v);
    w.u8(static_cast<std::uint8_t>(q.options.size()));
    for (const auto& o : q.options) {
        const auto desc = o.description.substr(0, std::min(o.description.size(), kDescMax));
        w.u8(o.id);
        w.u8(static_cast<std::uint8_t>(desc.size()));
        w.chars(desc);
        w.f32(o.estimated_cost_detour_m);
        w.f32(o.risk_score);
    }
    if (with_roi) {
        w.u16(static_cast<std::uint16_t>(q.roi.size()));
        w.bytes(q.roi);
    } else {
        w.u16(0);
    }
    if (!w.ok()) {
        return std::unexpected{WireError::NoRoom};
    }
    w.u16(crc16(w.written()));
    if (!w.ok()) {
        return std::unexpected{WireError::NoRoom};
    }
    return w.written();
}

std::expected<DecodedQuery, WireError>
unpack_query(std::span<const std::byte> frame) noexcept {
    if (frame.size() < kQueryFixed + 4) return std::unexpected{WireError::Short};
    if (frame[0] != kMagicQuery)        return std::unexpected{WireError::Magic};
    if (frame[1] != kWireVersion)       return std::unexpected{WireError::Version};

    const auto body = frame.first(frame.size() - 2);
    const auto got  = static_cast<std::uint16_t>(
        std::to_integer<std::uint16_t>(frame[frame.size() - 2]) |
        (std::to_integer<std::uint16_t>(frame[frame.size() - 1]) << 8));
    if (got != crc16(body)) return std::unexpected{WireError::Crc};

    Reader r{body, 2};
    DecodedQuery q;
    q.flags     = r.u8();
    q.query_id  = r.u16();
    q.timestamp = std::chrono::milliseconds{r.u32()};
    q.deadline  = std::chrono::milliseconds{r.u16()};
    q.trigger   = static_cast<Trigger>(r.u8());
    for (float& v : q.position) v = r.f32();
    for (float& v : q.velocity) v = r.f32();
    q.options_count = r.u8();
    if (!r.ok()) return std::unexpected{WireError::Short};
    if (q.options_count == 0 || q.options_count > kMaxOptions) {
        return std::unexpected{WireError::Field};
    }

    for (std::uint8_t i = 0; i < q.options_count; ++i) {
        Option o;
        o.id                = r.u8();
        const std::size_t n = r.u8();
        if (n > kDescMax) return std::unexpected{WireError::Field};
        o.description   = r.take_chars(n);   // дивиться в кадр, копії немає
        o.estimated_cost_detour_m = r.f32();
        o.risk_score    = r.f32();
        q.options[i]    = o;
    }

    const std::size_t roi_len = r.u16();
    if (!r.ok()) return std::unexpected{WireError::Short};
    if (roi_len > kRoiMax) return std::unexpected{WireError::Field};
    q.roi = r.take(roi_len);

    if (!r.ok()) return std::unexpected{WireError::Short};
    return q;
}

std::expected<std::span<const std::byte>, WireError>
pack_reply(const Reply& rep, std::span<std::byte> out) noexcept {
    if (out.size() < kReplyLen) return std::unexpected{WireError::NoRoom};

    Writer w{out};
    w.u8(std::to_integer<std::uint8_t>(kMagicReply));
    w.u8(std::to_integer<std::uint8_t>(kWireVersion));
    w.u16(rep.query_id);
    w.u8(rep.option_id);
    w.u32(static_cast<std::uint32_t>(rep.gcs_time.count()));
    w.u16(crc16(w.written()));
    if (!w.ok()) return std::unexpected{WireError::NoRoom};
    return w.written();
}

std::expected<Reply, WireError>
unpack_reply(std::span<const std::byte> frame) noexcept {
    if (frame.size() != kReplyLen) return std::unexpected{WireError::Short};
    if (frame[0] != kMagicReply)   return std::unexpected{WireError::Magic};
    if (frame[1] != kWireVersion)  return std::unexpected{WireError::Version};

    const auto body = frame.first(frame.size() - 2);
    const auto got  = static_cast<std::uint16_t>(
        std::to_integer<std::uint16_t>(frame[frame.size() - 2]) |
        (std::to_integer<std::uint16_t>(frame[frame.size() - 1]) << 8));
    if (got != crc16(body)) return std::unexpected{WireError::Crc};

    Reader r{body, 2};
    Reply rep;
    rep.query_id  = r.u16();
    rep.option_id = r.u8();
    rep.gcs_time  = std::chrono::milliseconds{r.u32()};
    if (!r.ok()) return std::unexpected{WireError::Short};
    return rep;
}

std::string_view to_string(WireError e) noexcept {
    switch (e) {
        case WireError::Short:   return "кадр обірвано";
        case WireError::Magic:   return "чужий кадр";
        case WireError::Version: return "інша версія протоколу";
        case WireError::Crc:     return "CRC не збігся";
        case WireError::Field:   return "поле поза діапазоном";
        case WireError::NoRoom:  return "не влазить у MTU";
    }
    return "?";
}

}  // namespace esc
