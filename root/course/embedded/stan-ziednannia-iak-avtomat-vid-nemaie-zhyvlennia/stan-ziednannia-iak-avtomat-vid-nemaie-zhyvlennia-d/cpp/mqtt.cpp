#include "mqtt.hpp"

namespace mqtt {
namespace {

/* Пише кадр у наданий буфер і сам стежить, чи не вилізли за межу. */
class Writer {
public:
    explicit Writer(std::span<std::byte> buf) : m_buf(buf) {}

    void put(std::uint8_t value)
    {
        if (m_pos >= m_buf.size()) {
            m_ok = false;
            return;
        }
        m_buf[m_pos++] = std::byte{value};
    }

    void putU16(std::uint16_t value)
    {
        put(static_cast<std::uint8_t>(value >> 8));
        put(static_cast<std::uint8_t>(value & 0xFF));
    }

    /* Рядок MQTT: два байти довжини (big-endian) і тіло. */
    void putString(std::string_view s)
    {
        putU16(static_cast<std::uint16_t>(s.size()));
        for (const char c : s) {
            put(static_cast<std::uint8_t>(c));
        }
    }

    void putVarint(std::uint32_t n)
    {
        do {
            auto digit = static_cast<std::uint8_t>(n % 128);
            n /= 128;
            if (n != 0) {
                digit |= 0x80;
            }
            put(digit);
        } while (n != 0);
    }

    void putBytes(std::span<const std::byte> data)
    {
        for (const std::byte b : data) {
            put(static_cast<std::uint8_t>(b));
        }
    }

    [[nodiscard]] std::expected<Frame, Error> done() const
    {
        if (!m_ok) {
            return std::unexpected(Error::BufferTooSmall);
        }
        return Frame{m_buf.first(m_pos)};
    }

private:
    std::span<std::byte> m_buf;
    std::size_t m_pos{0};
    bool m_ok{true};
};

} // namespace

std::expected<Frame, Error> connect(std::span<std::byte> buf, std::string_view clientId,
                                    std::string_view user, std::string_view password,
                                    std::chrono::seconds keepAlive)
{
    std::uint8_t flags = 0x02; /* Clean Session */
    std::size_t payload = 2 + clientId.size();

    if (!user.empty()) {
        flags |= 0x80;
        payload += 2 + user.size();
    }
    if (!password.empty()) {
        flags |= 0x40;
        payload += 2 + password.size();
    }

    /* 10 = "MQTT" + рівень + прапорці + keep-alive */
    const auto remaining = static_cast<std::uint32_t>(10 + payload);

    Writer w{buf};
    w.put(0x10); /* CONNECT */
    w.putVarint(remaining);
    w.putString("MQTT");
    w.put(0x04); /* рівень протоколу 3.1.1 */
    w.put(flags);
    w.putU16(static_cast<std::uint16_t>(keepAlive.count()));
    w.putString(clientId);
    if (!user.empty()) {
        w.putString(user);
    }
    if (!password.empty()) {
        w.putString(password);
    }
    return w.done();
}

std::expected<Frame, Error> publishQos1(std::span<std::byte> buf, std::string_view topic,
                                        std::span<const std::byte> payload,
                                        std::uint16_t packetId)
{
    const auto remaining = static_cast<std::uint32_t>(2 + topic.size() + 2 + payload.size());

    Writer w{buf};
    w.put(0x32); /* PUBLISH, QoS 1 — брокер мусить відповісти PUBACK */
    w.putVarint(remaining);
    w.putString(topic);
    w.putU16(packetId);
    w.putBytes(payload);
    return w.done();
}

std::expected<Frame, Error> pingReq(std::span<std::byte> buf)
{
    Writer w{buf};
    w.put(0xC0);
    w.put(0x00);
    return w.done();
}

std::expected<Frame, Error> disconnect(std::span<std::byte> buf)
{
    Writer w{buf};
    w.put(0xE0);
    w.put(0x00);
    return w.done();
}

Packet Decoder::build() const
{
    Packet pkt{};

    switch (m_header & 0xF0) {
    case 0x20:
        pkt.kind = Packet::Kind::ConnAck;
        pkt.code = (m_bodyLen >= 2) ? static_cast<std::uint8_t>(m_body[1]) : 0xFF;
        break;
    case 0x40:
        pkt.kind = Packet::Kind::PubAck;
        if (m_bodyLen >= 2) {
            pkt.id = static_cast<std::uint16_t>((static_cast<std::uint16_t>(m_body[0]) << 8) |
                                                static_cast<std::uint16_t>(m_body[1]));
        }
        break;
    case 0xD0:
        pkt.kind = Packet::Kind::PingResp;
        break;
    default:
        /* Наприклад PUBLISH від брокера: вузол ні на що не підписаний. */
        pkt.kind = Packet::Kind::Other;
        break;
    }
    return pkt;
}

std::optional<Packet> Decoder::feed(std::byte byte)
{
    const auto value = static_cast<std::uint8_t>(byte);

    switch (m_phase) {
    case Phase::Header:
        m_header = value;
        m_remaining = 0;
        m_multiplier = 1;
        m_lenBytes = 0;
        m_bodyLen = 0;
        m_phase = Phase::Length;
        return std::nullopt;

    case Phase::Length:
        m_remaining += static_cast<std::uint32_t>(value & 0x7F) * m_multiplier;
        m_multiplier *= 128;
        if (++m_lenBytes > 4) { /* довжина не буває довшою за 4 байти */
            reset();
            return Packet{Packet::Kind::Broken, 0, 0};
        }
        if ((value & 0x80) != 0) {
            return std::nullopt;
        }
        if (m_remaining == 0) {
            const Packet pkt = build();
            reset();
            return pkt;
        }
        m_phase = Phase::Body;
        return std::nullopt;

    default:
        if (m_bodyLen < m_body.size()) {
            m_body[m_bodyLen++] = byte; /* довгі тіла нам не потрібні */
        }
        if (--m_remaining == 0) {
            const Packet pkt = build();
            reset();
            return pkt;
        }
        return std::nullopt;
    }
}

} // namespace mqtt
