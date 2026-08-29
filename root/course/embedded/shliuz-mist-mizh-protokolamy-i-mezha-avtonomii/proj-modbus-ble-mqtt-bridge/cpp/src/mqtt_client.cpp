#include "mqtt_client.hpp"

#include <array>
#include <cstring>
#include <format>
#include <memory>

#include <netdb.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <sys/socket.h>

namespace gw {
namespace {

constexpr std::uint8_t kConnect = 0x10;
constexpr std::uint8_t kConnack = 0x20;
constexpr std::uint8_t kPublish = 0x30;
constexpr std::uint8_t kPuback = 0x40;
constexpr std::uint8_t kPingreq = 0xC0;
constexpr std::uint8_t kPingresp = 0xD0;
constexpr std::uint8_t kDisconnect = 0xE0;

constexpr std::size_t kMaxPacket = 1024;
constexpr auto kAckTimeout = std::chrono::seconds{5};

// Довжина решти пакета — змінне ціле по 7 біт на байт, старший біт «є ще».
void appendRemainingLength(std::vector<std::uint8_t>& out, std::size_t length) {
    do {
        auto byte = static_cast<std::uint8_t>(length % 128);
        length /= 128;
        if (length > 0) {
            byte |= 0x80;
        }
        out.push_back(byte);
    } while (length > 0);
}

void appendString(std::vector<std::uint8_t>& out, std::string_view text) {
    out.push_back(static_cast<std::uint8_t>(text.size() >> 8));
    out.push_back(static_cast<std::uint8_t>(text.size() & 0xFF));
    out.insert(out.end(), text.begin(), text.end());
}

Fd tcpConnect(const std::string& host, const std::string& port, std::chrono::milliseconds timeout) {
    addrinfo hints{};
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    addrinfo* list = nullptr;
    if (::getaddrinfo(host.c_str(), port.c_str(), &hints, &list) != 0) {
        throw MqttError{std::format("{} не розв'язується", host)};
    }
    // Список адрес звільняється в будь-якому разі — і на виході, і на винятку.
    const std::unique_ptr<addrinfo, decltype(&::freeaddrinfo)> guard{list, &::freeaddrinfo};

    for (const addrinfo* ai = list; ai != nullptr; ai = ai->ai_next) {
        Fd fd{::socket(ai->ai_family, ai->ai_socktype | SOCK_NONBLOCK, ai->ai_protocol)};
        if (!fd.valid()) {
            continue;
        }
        if (::connect(fd.get(), ai->ai_addr, ai->ai_addrlen) != 0) {
            if (errno != EINPROGRESS) {
                continue;
            }
            ::pollfd pfd{fd.get(), POLLOUT, 0};
            if (::poll(&pfd, 1, static_cast<int>(timeout.count())) != 1) {
                continue;
            }
            int error = 0;
            socklen_t length = sizeof(error);
            if (::getsockopt(fd.get(), SOL_SOCKET, SO_ERROR, &error, &length) != 0 || error != 0) {
                continue;
            }
        }
        // Телеметрія — короткі пакети; затримка Nagle тут лише псує реакцію.
        const int one = 1;
        ::setsockopt(fd.get(), IPPROTO_TCP, TCP_NODELAY, &one, sizeof(one));
        return fd;
    }
    throw MqttError{std::format("до {}:{} не достукатися", host, port)};
}

}  // namespace

MqttClient::MqttClient(const std::string& host, const std::string& port, std::string_view clientId,
                       std::chrono::seconds keepAlive)
    : fd_{tcpConnect(host, port, std::chrono::milliseconds{5000})}, keepAlive_{keepAlive} {
    std::vector<std::uint8_t> body;
    appendString(body, "MQTT");
    body.push_back(0x04);  // рівень протоколу 4 = MQTT 3.1.1
    body.push_back(0x02);  // clean session: черга живе в нас, а не в брокері
    body.push_back(static_cast<std::uint8_t>(keepAlive.count() >> 8));
    body.push_back(static_cast<std::uint8_t>(keepAlive.count() & 0xFF));
    appendString(body, clientId);

    std::vector<std::uint8_t> packet{kConnect};
    appendRemainingLength(packet, body.size());
    packet.insert(packet.end(), body.begin(), body.end());
    send(packet);

    const auto answer = readPacket(std::chrono::steady_clock::now() + kAckTimeout);
    if (!answer || answer->type != kConnack || answer->payload.size() < 2) {
        throw MqttError{"брокер не відповів на CONNECT"};
    }
    if (answer->payload[1] != 0x00) {
        // 0x04 — хибні дані входу, 0x05 — не авторизовано.
        throw MqttError{std::format("брокер відмовив, код 0x{:02X}", answer->payload[1])};
    }
}

MqttClient::~MqttClient() {
    if (!fd_.valid()) {
        return;
    }
    try {
        const std::array<std::uint8_t, 2> packet{kDisconnect, 0x00};
        fd_.writeAll(std::as_bytes(std::span{packet}));
    } catch (const std::exception&) {
        // Прощання — ввічливість, а не обов'язок: сокет закриє Fd.
    }
}

void MqttClient::send(std::span<const std::uint8_t> packet) {
    fd_.writeAll(std::as_bytes(packet));
    lastTx_ = std::chrono::steady_clock::now();
}

std::optional<MqttClient::Packet> MqttClient::readPacket(
    std::chrono::steady_clock::time_point deadline) {
    std::array<std::uint8_t, 1> header{};
    if (!fd_.readExact(std::as_writable_bytes(std::span{header}), deadline)) {
        return std::nullopt;
    }

    std::size_t remaining = 0;
    std::size_t multiplier = 1;
    for (int i = 0; i < 4; ++i) {
        std::array<std::uint8_t, 1> byte{};
        if (!fd_.readExact(std::as_writable_bytes(std::span{byte}), deadline)) {
            throw MqttError{"пакет обірвано на довжині"};
        }
        remaining += static_cast<std::size_t>(byte[0] & 0x7F) * multiplier;
        if ((byte[0] & 0x80) == 0) {
            break;
        }
        multiplier *= 128;
        if (i == 3) {
            throw MqttError{"довжина понад чотири байти — потік зіпсовано"};
        }
    }
    if (remaining > kMaxPacket) {
        throw MqttError{std::format("пакет на {} байтів завеликий", remaining)};
    }

    Packet packet;
    packet.type = static_cast<std::uint8_t>(header[0] & 0xF0);
    packet.payload.resize(remaining);
    if (remaining > 0 &&
        !fd_.readExact(std::as_writable_bytes(std::span{packet.payload}), deadline)) {
        throw MqttError{"пакет обірвано на тілі"};
    }
    return packet;
}

void MqttClient::publishQos1(std::string_view topic, std::string_view payload) {
    const std::uint16_t packetId = nextPacketId_++;
    if (nextPacketId_ == 0) {
        nextPacketId_ = 1;  // нуль як ідентифікатор заборонено
    }

    std::vector<std::uint8_t> packet{static_cast<std::uint8_t>(kPublish | 0x02)};  // QoS 1
    appendRemainingLength(packet, 2 + topic.size() + 2 + payload.size());
    appendString(packet, topic);
    packet.push_back(static_cast<std::uint8_t>(packetId >> 8));
    packet.push_back(static_cast<std::uint8_t>(packetId & 0xFF));
    packet.insert(packet.end(), payload.begin(), payload.end());
    send(packet);

    // Чекаємо саме на PUBACK нашого пакета; усе, що прилетить попереду
    // (наприклад, відповідь на попередній PINGREQ), просто вичитуємо.
    const auto deadline = std::chrono::steady_clock::now() + kAckTimeout;
    for (;;) {
        const auto answer = readPacket(deadline);
        if (!answer) {
            throw MqttError{std::format("брокер не підтвердив пакет {}", packetId)};
        }
        if (answer->type == kPingresp) {
            awaitingPingResp_ = false;
            continue;
        }
        if (answer->type == kPuback && answer->payload.size() >= 2) {
            const auto acked =
                static_cast<std::uint16_t>((answer->payload[0] << 8) | answer->payload[1]);
            if (acked == packetId) {
                return;
            }
        }
        // Чужі пакети мовчки ковтаємо: ми ні на що не підписані.
    }
}

void MqttClient::serviceKeepAlive() {
    const auto now = std::chrono::steady_clock::now();

    if (awaitingPingResp_ && now > pingDeadline_) {
        throw MqttError{"брокер не відповів на PINGREQ"};
    }

    if (!awaitingPingResp_ && now - lastTx_ >= keepAlive_ / 2) {
        const std::array<std::uint8_t, 2> packet{kPingreq, 0x00};
        send(packet);
        awaitingPingResp_ = true;
        pingDeadline_ = now + kAckTimeout;
    }

    // Вичитуємо те, що вже лежить у сокеті, не блокуючись.
    while (fd_.waitReadable(std::chrono::milliseconds{0})) {
        const auto answer = readPacket(std::chrono::steady_clock::now() + std::chrono::seconds{1});
        if (!answer) {
            break;
        }
        if (answer->type == kPingresp) {
            awaitingPingResp_ = false;
        }
    }
}

}  // namespace gw
