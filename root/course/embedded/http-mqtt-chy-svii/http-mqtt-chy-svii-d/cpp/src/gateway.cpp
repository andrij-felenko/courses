// gateway.cpp — та сама ціна власного протоколу: приймати кадри нікому,
// тож шлюз пишемо самі. Слухає UDP, перевіряє CRC, розбирає структуру,
// відсіює дублікати після втраченого ACK і підтверджує кожен кадр.
//
// Збірка: c++ -std=c++23 -O2 -Wall -Wextra -o gateway gateway.cpp codec.cpp
#include <array>
#include <cerrno>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <format>
#include <iostream>
#include <netdb.h>
#include <netinet/in.h>
#include <optional>
#include <string>
#include <sys/socket.h>
#include <unistd.h>
#include <unordered_map>

#include "codec.hpp"

namespace {

// Дескриптор слухавки теж під RAII: аварійний вихід не лишає відкритого fd.
class ListeningSocket {
public:
    static std::optional<ListeningSocket> bindTo(const std::string& port)
    {
        addrinfo hints{};
        hints.ai_family = AF_INET6;   // один сокет на IPv6 і IPv4-mapped
        hints.ai_socktype = SOCK_DGRAM;
        hints.ai_flags = AI_PASSIVE;

        addrinfo* found = nullptr;
        if (::getaddrinfo(nullptr, port.c_str(), &hints, &found) != 0) {
            return std::nullopt;
        }
        struct Guard {
            addrinfo* list;
            ~Guard() { ::freeaddrinfo(list); }
        } guard{found};

        for (const addrinfo* ai = found; ai != nullptr; ai = ai->ai_next) {
            const int fd = ::socket(ai->ai_family, ai->ai_socktype, ai->ai_protocol);
            if (fd < 0) {
                continue;
            }
            int off = 0;
            ::setsockopt(fd, IPPROTO_IPV6, IPV6_V6ONLY, &off, sizeof off);
            if (::bind(fd, ai->ai_addr, ai->ai_addrlen) == 0) {
                return ListeningSocket{fd};
            }
            ::close(fd);
        }
        return std::nullopt;
    }

    ListeningSocket(const ListeningSocket&) = delete;
    ListeningSocket& operator=(const ListeningSocket&) = delete;
    ListeningSocket(ListeningSocket&& other) noexcept : fd_{other.fd_} { other.fd_ = -1; }
    ListeningSocket& operator=(ListeningSocket&&) = delete;
    ~ListeningSocket() { if (fd_ >= 0) ::close(fd_); }

    [[nodiscard]] int fd() const noexcept { return fd_; }

private:
    explicit ListeningSocket(int fd) noexcept : fd_{fd} {}
    int fd_{-1};
};

std::string peerKey(const sockaddr_storage& from, socklen_t len)
{
    std::array<char, NI_MAXHOST> host{};
    std::array<char, NI_MAXSERV> serv{};
    if (::getnameinfo(reinterpret_cast<const sockaddr*>(&from), len,
                      host.data(), host.size(), serv.data(), serv.size(),
                      NI_NUMERICHOST | NI_NUMERICSERV) != 0) {
        return "?:?";
    }
    return std::format("{}:{}", host.data(), serv.data());
}

std::string celsius(std::int16_t hundredths)
{
    return std::format("{}.{:02}", hundredths / 100, std::abs(hundredths % 100));
}

}  // namespace

int main(int argc, char** argv)
{
    const std::string port = argc > 1 ? argv[1] : "9000";

    const auto socket = ListeningSocket::bindTo(port);
    if (!socket) {
        std::cerr << std::format("gateway: не сів на порт {} — {}\n",
                                 port, std::strerror(errno));
        return 1;
    }
    std::cout << std::format("gateway: слухаю UDP {}\n", port);

    // Дублікати неминучі: якщо ACK загубився, вузол шле той самий кадр удруге.
    // Тримаємо останній підтверджений номер на кожного відправника — цього
    // досить, бо ARQ у вузла stop-and-wait і в польоті завжди один кадр.
    std::unordered_map<std::string, std::uint16_t> last_seq;

    for (;;) {
        std::array<std::byte, 128> buffer{};
        sockaddr_storage from{};
        socklen_t from_len = sizeof from;

        const auto got = ::recvfrom(socket->fd(), buffer.data(), buffer.size(), 0,
                                    reinterpret_cast<sockaddr*>(&from), &from_len);
        if (got < 0) {
            if (errno == EINTR) {
                continue;
            }
            std::cerr << std::format("gateway: recvfrom — {}\n", std::strerror(errno));
            return 1;
        }

        const auto datagram =
            std::span<const std::byte>{buffer}.first(static_cast<std::size_t>(got));
        const std::string key = peerKey(from, from_len);

        const auto packet = telemetry::decodeTelemetry(datagram);
        if (!packet) {
            // Побитий або чужий кадр не підтверджуємо: хай вузол повторить.
            std::cerr << std::format("gateway: {} — кадр відкинуто ({})\n",
                                     key, telemetry::describe(packet.error()));
            continue;
        }

        auto [slot, fresh] = last_seq.try_emplace(key, packet->seq);
        const bool duplicate = !fresh && slot->second == packet->seq;
        slot->second = packet->seq;

        if (duplicate) {
            std::cout << std::format("{} #{} — повтор, у базу не пишемо\n",
                                     key, packet->seq);
        } else {
            std::cout << std::format("{} #{} ts={}  {} °C  {}.{:02} %  {} мВ\n",
                                     key, packet->seq, packet->timestamp,
                                     celsius(packet->temperature),
                                     packet->humidity / 100, packet->humidity % 100,
                                     packet->vbat_mv);
        }
        std::cout.flush();

        // Підтверджуємо і повтор теж: саме втрата ACK його й спричинила.
        std::array<std::byte, telemetry::kAckSize> ack{};
        const auto encoded = telemetry::encodeAck(packet->seq, ack);
        if (encoded && ::sendto(socket->fd(), encoded->data(), encoded->size(), 0,
                                reinterpret_cast<const sockaddr*>(&from), from_len) < 0) {
            std::cerr << std::format("gateway: ACK не пішов — {}\n", std::strerror(errno));
        }
    }
}
