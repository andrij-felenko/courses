#include <iostream>
#include <string_view>
#include <expected>
#include <system_error>
#include <memory>
#include <cstring>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

class SafeSocket {
private:
    int fd_{-1};

public:
    explicit SafeSocket(int fd) noexcept : fd_{fd} {}
    ~SafeSocket() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    SafeSocket(const SafeSocket&) = delete;
    SafeSocket& operator=(const SafeSocket&) = delete;

    SafeSocket(SafeSocket&& other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }

    SafeSocket& operator=(SafeSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) {
                ::close(fd_);
            }
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

[[nodiscard]] std::expected<SafeSocket, std::error_code>
create_configured_server(uint16_t port) noexcept {
    int raw_fd = ::socket(AF_INET, SOCK_STREAM, 0);
    if (raw_fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    SafeSocket sock(raw_fd);

    // 1. Дозволити швидкий bind при TIME_WAIT
    const int reuse_addr = 1;
    if (::setsockopt(sock.get(), SOL_SOCKET, SO_REUSEADDR, &reuse_addr, sizeof(reuse_addr)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    // 2. Вимкнути алгоритм Нейгла
    const int nodelay = 1;
    if (::setsockopt(sock.get(), IPPROTO_TCP, TCP_NODELAY, &nodelay, sizeof(nodelay)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    // 3. Встановити таймаут непідтверджених даних (10 000 мс)
    const unsigned int timeout_ms = 10000;
    if (::setsockopt(sock.get(), IPPROTO_TCP, TCP_USER_TIMEOUT, &timeout_ms, sizeof(timeout_ms)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(port);

    if (::bind(sock.get(), reinterpret_cast<const sockaddr*>(&addr), sizeof(addr)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    if (::listen(sock.get(), 1024) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return sock;
}
