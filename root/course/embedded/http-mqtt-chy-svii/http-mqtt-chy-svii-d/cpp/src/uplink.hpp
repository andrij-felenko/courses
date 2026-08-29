// uplink.hpp — «постріл і сон»: одна UDP-датаграма, підтвердження, спул.
//
// Дескриптор сокета тримає UdpSocket: закриває його деструктор, тож жодних
// гілок «goto out» і жодного шансу лишити відкритий fd на шляху помилки.
#pragma once

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <string>
#include <string_view>
#include <sys/socket.h>

#include "frame.hpp"

namespace telemetry {

using namespace std::chrono_literals;

inline constexpr auto kArqTimeout = 500ms;
inline constexpr int  kArqAttempts = 3;
inline constexpr std::size_t kSpoolCapacity = 256;  // 4 КБ — сторінка Flash

using Frame = std::array<std::byte, kTelemetrySize>;

enum class NetError {
    Resolve,   // ім'я не розв'язалося
    Open,      // сокет не відкрився
    Send,      // датаграма не пішла
    Receive,   // сокет зламався на прийомі
    Timeout,   // відповіді не було
};

[[nodiscard]] std::string_view describe(NetError error) noexcept;

class UdpSocket {
public:
    [[nodiscard]] static std::expected<UdpSocket, NetError>
    to(std::string_view host, std::string_view port);

    UdpSocket(const UdpSocket&) = delete;
    UdpSocket& operator=(const UdpSocket&) = delete;
    UdpSocket(UdpSocket&& other) noexcept;
    UdpSocket& operator=(UdpSocket&& other) noexcept;
    ~UdpSocket();

    [[nodiscard]] std::expected<void, NetError>
    send(std::span<const std::byte> frame) const;

    // Чекає датаграму САМЕ від нашого сервера, не довше за timeout.
    // Чужі датаграми відкидає мовчки, не з'їдаючи весь час очікування.
    [[nodiscard]] std::expected<std::span<std::byte>, NetError>
    receive(std::span<std::byte> buffer, std::chrono::milliseconds timeout) const;

private:
    UdpSocket(int fd, const sockaddr_storage& peer, socklen_t peer_len) noexcept;

    int fd_{-1};
    sockaddr_storage peer_{};
    socklen_t peer_len_{0};
};

class Uplink {
public:
    Uplink(UdpSocket socket, std::string spool_path, std::uint16_t first_seq);

    // true — сервер підтвердив; false — кадр відкладено у спул.
    bool send(const Sample& sample);

    // Віддає відкладені кадри; повертає, скільки з них підтверджено.
    std::size_t flushSpool();

    [[nodiscard]] std::uint16_t seq() const noexcept { return seq_; }
    [[nodiscard]] std::chrono::milliseconds transmitTime() const noexcept { return tx_; }

private:
    bool sendWithRetries(const Frame& frame);
    std::span<Frame> loadSpool(std::size_t& dropped);
    void storeSpool(std::span<const Frame> frames) const;

    UdpSocket socket_;
    std::string spool_path_;
    std::uint16_t seq_;
    std::chrono::milliseconds tx_{0};
    std::array<Frame, kSpoolCapacity> spool_{};
};

}  // namespace telemetry
