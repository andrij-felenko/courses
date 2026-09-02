#pragma once

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <optional>
#include <span>
#include <string_view>

/* Мінімум MQTT 3.1.1, якого вистачає вузлу телеметрії: CONNECT/CONNACK,
   PUBLISH QoS 1/PUBACK, PINGREQ/PINGRESP, DISCONNECT. */
namespace mqtt {

enum class Error { BufferTooSmall };

using Frame = std::span<const std::byte>;

/* Складачі пишуть у наданий буфер і віддають готовий зріз кадру. */
std::expected<Frame, Error> connect(std::span<std::byte> buf, std::string_view clientId,
                                    std::string_view user, std::string_view password,
                                    std::chrono::seconds keepAlive);
std::expected<Frame, Error> publishQos1(std::span<std::byte> buf, std::string_view topic,
                                        std::span<const std::byte> payload,
                                        std::uint16_t packetId);
std::expected<Frame, Error> pingReq(std::span<std::byte> buf);
std::expected<Frame, Error> disconnect(std::span<std::byte> buf);

struct Packet {
    enum class Kind : std::uint8_t {
        ConnAck,
        PubAck,
        PingResp,
        Other,
        Broken /* потік не схожий на MQTT — сокет треба перевідкрити */
    };

    Kind kind{Kind::Other};
    std::uint8_t code{0};  /* код повернення CONNACK */
    std::uint16_t id{0};   /* ідентифікатор PUBACK */
};

class Decoder {
public:
    void reset() noexcept { *this = Decoder{}; }

    /* Згодовує один байт; значення є → зібрано цілий пакет. */
    std::optional<Packet> feed(std::byte byte);

private:
    enum class Phase : std::uint8_t { Header, Length, Body };

    [[nodiscard]] Packet build() const;

    Phase m_phase{Phase::Header};
    std::uint8_t m_header{0};
    std::uint32_t m_remaining{0};
    std::uint32_t m_multiplier{1};
    std::uint8_t m_lenBytes{0};
    std::array<std::byte, 8> m_body{};
    std::uint8_t m_bodyLen{0};
};

} // namespace mqtt
