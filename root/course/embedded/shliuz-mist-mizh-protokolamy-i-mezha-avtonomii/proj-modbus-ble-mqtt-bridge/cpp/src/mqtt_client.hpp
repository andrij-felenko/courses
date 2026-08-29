#pragma once

#include <chrono>
#include <cstdint>
#include <optional>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

#include "posix_fd.hpp"

namespace gw {

class MqttError : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

// Мінімальний клієнт MQTT 3.1.1: CONNECT, PUBLISH з QoS 1, PINGREQ, DISCONNECT
// — рівно те, що потрібно висхідному напрямку шлюза.
//
// QoS 1 тут не примха: черга віддає повідомлення лише після PUBACK, тож обрив
// у момент передавання коштує повтору, а не втраченого вимірювання.
//
// Конструктор або підключається, або кидає виняток — напівживого об'єкта не
// буває. На виробництві сокет обгортають у TLS; рамка пакетів від цього не
// міняється, тому тут чистий TCP, щоб було видно самі кадри протоколу.
class MqttClient {
public:
    MqttClient(const std::string& host, const std::string& port, std::string_view clientId,
               std::chrono::seconds keepAlive);
    ~MqttClient();

    MqttClient(const MqttClient&) = delete;
    MqttClient& operator=(const MqttClient&) = delete;

    // Повертається лише після PUBACK; MqttError означає, що канал треба піднімати заново.
    void publishQos1(std::string_view topic, std::string_view payload);

    // Шле PINGREQ, коли настав час, і вичитує те, що вже прилетіло. Мовчання у
    // відповідь — єдина ознака мертвого каналу, яку ми маємо: TCP-сокет може
    // мовчки вважатися живим ще довгі хвилини.
    void serviceKeepAlive();

private:
    struct Packet {
        std::uint8_t type{};
        std::vector<std::uint8_t> payload;
    };

    void send(std::span<const std::uint8_t> packet);
    std::optional<Packet> readPacket(std::chrono::steady_clock::time_point deadline);

    Fd fd_;
    std::chrono::seconds keepAlive_;
    std::chrono::steady_clock::time_point lastTx_;
    std::chrono::steady_clock::time_point pingDeadline_;
    std::uint16_t nextPacketId_{1};
    bool awaitingPingResp_{false};
};

}  // namespace gw
