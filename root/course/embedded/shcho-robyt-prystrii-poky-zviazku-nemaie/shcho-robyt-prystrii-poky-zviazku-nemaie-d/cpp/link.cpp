#include "link.hpp"

#include <algorithm>
#include <cmath>

#include "wire.hpp"

namespace cart {

namespace {

// Розкладка кадру: [0] тип · [1..4] сесія · [5..8] номер · [9..12] час
// відправника · [13..14] тяга · [15..16] кермо · [17] резерв ·
// [18..21] мітка автентичності · [22..23] CRC-16.
Frame build(FrameType type, std::uint32_t key, std::uint32_t session, std::uint32_t seq,
            Millis stamp, float throttle, float steering) noexcept {
    Frame f{};
    f[0] = static_cast<std::byte>(type);
    wire::putU32(f, 1, session);
    wire::putU32(f, 5, seq);
    wire::putU32(f, 9, static_cast<std::uint32_t>(stamp.count()));
    wire::putI16(f, 13, static_cast<std::int16_t>(std::lround(std::clamp(throttle, -1.0f, 1.0f) * 10000.0f)));
    wire::putI16(f, 15, static_cast<std::int16_t>(std::lround(std::clamp(steering, -1.0f, 1.0f) * 10000.0f)));
    wire::putU32(f, 18, wire::authTag(std::span{f}.first(18), key));
    wire::putU16(f, 22, wire::crc16(std::span{f}.first(22)));
    return f;
}

}  // namespace

std::string_view describe(LinkError e) noexcept {
    switch (e) {
    case LinkError::Length:  return "хибна довжина";
    case LinkError::Type:    return "невідомий тип";
    case LinkError::Crc:     return "CRC не збігся";
    case LinkError::Auth:    return "мітка автентичності хибна";
    case LinkError::Session: return "чужа або скасована сесія";
    case LinkError::Replay:  return "повтор старого кадру";
    case LinkError::Stale:   return "команда застаріла";
    }
    return "?";
}

std::expected<Command, LinkError> Link::accept(std::span<const std::byte> frame, Millis now) noexcept {
    if (frame.size() != kFrameSize) return std::unexpected(LinkError::Length);

    if (wire::u16(frame, 22) != wire::crc16(frame.first(22))) {
        ++rejects_.crc;
        return std::unexpected(LinkError::Crc);
    }
    if (wire::u32(frame, 18) != wire::authTag(frame.first(18), key_)) {
        ++rejects_.auth;
        return std::unexpected(LinkError::Auth);
    }

    const auto type = static_cast<FrameType>(std::to_integer<std::uint8_t>(frame[0]));
    const auto session = wire::u32(frame, 1);
    const auto seq = wire::u32(frame, 5);
    const Millis stamp{wire::u32(frame, 9)};

    if (type == FrameType::Hello) {
        // Нова сесія стирає все, що лишилося від старої: номери кадрів більше
        // не дійсні, а команди, застряглі в буферах передавача, — тим паче.
        session_ = session;
        lastSeq_ = seq;
        established_ = true;
        clockBias_ = stamp - now;
        ++accepted_;
        return Command{.type = type, .session = session, .seq = seq, .stamp = stamp};
    }
    if (type != FrameType::Command) return std::unexpected(LinkError::Type);

    if (!established_ || session != session_) {
        ++rejects_.session;
        return std::unexpected(LinkError::Session);
    }
    if (static_cast<std::int32_t>(seq - lastSeq_) <= 0) {
        ++rejects_.replay;
        return std::unexpected(LinkError::Replay);
    }
    // Вік команди міряємо в часовій шкалі відправника: зсув його годинника ми
    // запам'ятали на рукостисканні, а свій монотонний час підтягуємо окремо
    // й повільно, тому мішати ці дві шкали тут не можна.
    if ((now + clockBias_) - stamp > kMaxCommandAge) {
        ++rejects_.stale;
        return std::unexpected(LinkError::Stale);
    }

    lastSeq_ = seq;
    ++accepted_;
    return Command{.type = type,
                   .session = session,
                   .seq = seq,
                   .stamp = stamp,
                   .throttle = static_cast<float>(wire::i16(frame, 13)) / 10000.0f,
                   .steering = static_cast<float>(wire::i16(frame, 15)) / 10000.0f};
}

Frame Link::makeHello(std::uint32_t key, std::uint32_t session, Millis stamp) noexcept {
    return build(FrameType::Hello, key, session, 0, stamp, 0.0f, 0.0f);
}

Frame Link::makeCommand(std::uint32_t key, std::uint32_t session, std::uint32_t seq,
                        Millis stamp, float throttle, float steering) noexcept {
    return build(FrameType::Command, key, session, seq, stamp, throttle, steering);
}

}  // namespace cart
