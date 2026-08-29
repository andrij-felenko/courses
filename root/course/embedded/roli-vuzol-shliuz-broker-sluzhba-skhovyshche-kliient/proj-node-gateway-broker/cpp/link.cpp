#include "link.hpp"

#include <netdb.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <poll.h>
#include <sys/socket.h>
#include <unistd.h>

#include <array>
#include <cerrno>
#include <cstring>
#include <format>
#include <utility>

namespace field {

std::string_view describe(LinkError err) noexcept {
    switch (err) {
        case LinkError::Closed: return "шлюз закрив з'єднання";
        case LinkError::Io:     return "збій вводу-виводу";
    }
    return "невідомий збій каналу";
}

TcpLink::~TcpLink() {
    if (fd_ >= 0) {
        ::close(fd_);
    }
}

TcpLink::TcpLink(TcpLink&& other) noexcept
    : fd_(std::exchange(other.fd_, -1)), framer_(std::move(other.framer_)) {}

TcpLink& TcpLink::operator=(TcpLink&& other) noexcept {
    if (this != &other) {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = std::exchange(other.fd_, -1);
        framer_ = std::move(other.framer_);
    }
    return *this;
}

std::expected<TcpLink, std::string> TcpLink::connect(const std::string& host,
                                                     const std::string& port) {
    addrinfo hints{};
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;

    addrinfo* list = nullptr;
    if (const int rc = ::getaddrinfo(host.c_str(), port.c_str(), &hints, &list); rc != 0) {
        return std::unexpected(std::format("адресу {}:{} не розібрано — {}", host, port,
                                           ::gai_strerror(rc)));
    }

    int fd = -1;
    for (addrinfo* ai = list; ai != nullptr; ai = ai->ai_next) {
        fd = ::socket(ai->ai_family, ai->ai_socktype, ai->ai_protocol);
        if (fd < 0) {
            continue;
        }
        if (::connect(fd, ai->ai_addr, ai->ai_addrlen) == 0) {
            break;
        }
        ::close(fd);
        fd = -1;
    }
    ::freeaddrinfo(list);

    if (fd < 0) {
        return std::unexpected(std::format("шлюз {}:{} не відповідає — {}", host, port,
                                           std::strerror(errno)));
    }

    // Кадр керування короткий; накопичення в Nagle тут стало б чистою затримкою.
    const int one = 1;
    ::setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &one, sizeof one);

    return TcpLink{fd};
}

std::expected<void, LinkError> TcpLink::send(const Wire& wire) {
    std::size_t sent = 0;
    while (sent < wire.size()) {
        const ssize_t n = ::send(fd_, wire.data() + sent, wire.size() - sent, MSG_NOSIGNAL);
        if (n > 0) {
            sent += static_cast<std::size_t>(n);
            continue;
        }
        if (n < 0 && errno == EINTR) {
            continue;
        }
        return std::unexpected(n == 0 ? LinkError::Closed : LinkError::Io);
    }
    return {};
}

std::expected<std::optional<Wire>, LinkError> TcpLink::read_frame(
    std::chrono::milliseconds timeout) {
    // Спершу — те, що вже лежить у кадрувальнику: одне читання сокета
    // часто приносить кілька кадрів одразу.
    if (auto ready = framer_.next()) {
        return ready;
    }

    pollfd pfd{.fd = fd_, .events = POLLIN, .revents = 0};
    const int pr = ::poll(&pfd, 1, static_cast<int>(timeout.count()));
    if (pr == 0 || (pr < 0 && errno == EINTR)) {
        return std::optional<Wire>{};   // тиша або сигнал — канал цілий
    }
    if (pr < 0) {
        return std::unexpected(LinkError::Io);
    }

    std::array<std::byte, 256> chunk{};
    const ssize_t n = ::recv(fd_, chunk.data(), chunk.size(), 0);
    if (n == 0) {
        return std::unexpected(LinkError::Closed);
    }
    if (n < 0) {
        if (errno == EINTR || errno == EAGAIN) {
            return std::optional<Wire>{};
        }
        return std::unexpected(LinkError::Io);
    }

    framer_.feed(std::span<const std::byte>(chunk.data(), static_cast<std::size_t>(n)));
    return framer_.next();
}

}  // namespace field
