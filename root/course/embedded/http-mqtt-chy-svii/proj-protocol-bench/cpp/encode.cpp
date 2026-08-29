// Реалізація трьох пакувальників (C++23).
#include "encode.hpp"

#include "bytes.hpp"

#include <array>
#include <format>

namespace telem {
namespace {

// Remaining Length у MQTT — змінне кодування по 7 біт на байт, старший біт
// означає «є продовження». До 127 байтів вистачає одного байта, далі двох,
// і так до чотирьох (268 435 455).
constexpr bool writeRemainingLength(ByteWriter& w, std::size_t remaining) noexcept
{
    if (remaining > 268'435'455U) {
        return false;
    }
    do {
        auto digit = static_cast<std::uint8_t>(remaining % 128U);
        remaining /= 128U;
        if (remaining > 0) {
            digit = static_cast<std::uint8_t>(digit | 0x80U);
        }
        w.u8(digit);
    } while (remaining > 0);
    return true;
}

}  // namespace

std::expected<std::string_view, EncodeError>
buildHttpPost(const Sample& s,
              std::string_view host,
              std::string_view token,
              std::span<char> out) noexcept
{
    // Тіло доводиться зібрати повністю ще до заголовків: його довжина йде в
    // Content-Length, тобто в рядок, який фізично лежить ПЕРЕД тілом. Звідси
    // й другий буфер на стеку — обійти це в HTTP/1.1 без chunked нічим.
    std::array<char, 96> json{};
    const auto body_res = std::format_to_n(
        json.data(), static_cast<std::ptrdiff_t>(json.size()),
        R"({{"ts":{},"t":{:.2f},"h":{:.2f},"vbat":{}}})",
        s.timestamp_s,
        static_cast<double>(s.temp_centi_c) / 100.0,
        static_cast<double>(s.humidity_pct) / 100.0,
        s.vbat_mv);

    // format_to_n повертає довжину, яка була б ПОТРІБНА, а пише скільки
    // влізло: більше за розмір буфера означає мовчазне обрізання.
    if (body_res.size < 0 || static_cast<std::size_t>(body_res.size) > json.size()) {
        return std::unexpected(EncodeError::Formatting);
    }
    const std::string_view body{json.data(), static_cast<std::size_t>(body_res.size)};

    const auto res = std::format_to_n(
        out.data(), static_cast<std::ptrdiff_t>(out.size()),
        "POST /api/v1/telemetry HTTP/1.1\r\n"
        "Host: {}\r\n"
        "Authorization: Bearer {}\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
        "{}",
        host, token, body.size(), body);

    if (res.size < 0 || static_cast<std::size_t>(res.size) > out.size()) {
        return std::unexpected(EncodeError::BufferTooSmall);
    }
    return std::string_view{out.data(), static_cast<std::size_t>(res.size)};
}

std::expected<std::span<const std::uint8_t>, EncodeError>
buildMqttPublishQos1(const Sample& s,
                     std::string_view topic,
                     std::uint16_t packet_id,
                     std::span<std::uint8_t> out) noexcept
{
    // Тему для PUBLISH перевіряємо самі: шаблони '+' і '#' — синтаксис
    // ПІДПИСКИ, і брокер розірве зʼєднання, побачивши їх у публікації.
    if (topic.empty() || topic.size() > 0xFFFFU || topic.find_first_of("+#") != std::string_view::npos) {
        return std::unexpected(EncodeError::BadTopic);
    }
    // Packet Identifier 0 для QoS 1 заборонений: такий пакет неможливо
    // підтвердити через PUBACK.
    if (packet_id == 0) {
        return std::unexpected(EncodeError::BadPacketId);
    }

    std::array<char, 48> payload{};
    const auto payload_res = std::format_to_n(
        payload.data(), static_cast<std::ptrdiff_t>(payload.size()),
        R"({{"t":{},"h":{},"v":{}}})",
        s.temp_centi_c, s.humidity_pct, s.vbat_mv);

    if (payload_res.size < 0 || static_cast<std::size_t>(payload_res.size) > payload.size()) {
        return std::unexpected(EncodeError::Formatting);
    }
    const std::string_view body{payload.data(), static_cast<std::size_t>(payload_res.size)};

    // Змінний заголовок: довжина теми (2 Б) + тема + Packet ID (2 Б для QoS 1).
    const std::size_t remaining = 2U + topic.size() + 2U + body.size();

    ByteWriter w{out};
    w.u8(0x32);  // PUBLISH, DUP=0, QoS=1, RETAIN=0
    if (!writeRemainingLength(w, remaining)) {
        return std::unexpected(EncodeError::BufferTooSmall);
    }
    w.u16be(static_cast<std::uint16_t>(topic.size()))
     .raw(topic)
     .u16be(packet_id)
     .raw(body);

    if (!w.ok()) {
        return std::unexpected(EncodeError::BufferTooSmall);
    }
    return w.written();
}

std::expected<std::span<const std::uint8_t>, EncodeError>
buildBinaryFrame(const Sample& s, std::uint16_t seq, std::span<std::uint8_t> out) noexcept
{
    ByteWriter w{out};
    w.u8(kMagic)
     .u8(kTypeTelemetry)
     .u16le(seq)
     .u32le(s.timestamp_s)
     .i16le(s.temp_centi_c)
     .u16le(s.humidity_pct)
     .u16le(s.vbat_mv);

    if (!w.ok() || w.size() != kFrameCrcLen) {
        return std::unexpected(EncodeError::BufferTooSmall);
    }

    // CRC рахуємо рівно по тому, що вже лягло в буфер, — тобто по 14 байтах
    // без самого поля контрольної суми.
    w.u16le(crc16Ccitt(w.written()));

    if (!w.ok() || w.size() != kFrameSize) {
        return std::unexpected(EncodeError::BufferTooSmall);
    }
    return w.written();
}

}  // namespace telem
