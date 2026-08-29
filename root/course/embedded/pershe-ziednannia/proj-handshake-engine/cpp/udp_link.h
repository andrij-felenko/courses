#pragma once

#include <cstdint>
#include <span>
#include <string>

#include <netinet/in.h>

// UDP-кінець станції: слухає локальний порт і відповідає туди, звідки прийшов
// останній кадр (саме так працює зв'язка з sim_vehicle.py --out і з
// радіомодемом за мережевим мостом). Дескриптор живе за RAII: жодних
// close(fd) у гілках помилок.
class UdpLink {
public:
    UdpLink(const std::string& bind_host, std::uint16_t bind_port);
    ~UdpLink();

    UdpLink(const UdpLink&) = delete;
    UdpLink& operator=(const UdpLink&) = delete;

    // Чекає до timeout_ms на дейтаграму; 0 означає «тиша», а не помилку.
    std::size_t receive(std::span<std::uint8_t> out, int timeout_ms);

    // Пише кадр відомому кореспондентові; поки його немає — тихо ковтає.
    void send(std::span<const std::uint8_t> frame);

    [[nodiscard]] bool hasPeer() const noexcept { return m_has_peer; }
    [[nodiscard]] std::string peerName() const;

    // Повертає true один раз після зміни кореспондента — щоб журнал сказав це раз.
    bool takePeerUpdate() noexcept;

private:
    int m_fd{-1};
    sockaddr_in m_peer{};
    bool m_has_peer{false};
    bool m_peer_fresh{false};
};
