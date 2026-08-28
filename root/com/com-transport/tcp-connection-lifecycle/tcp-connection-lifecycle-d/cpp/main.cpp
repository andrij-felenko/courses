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

class ServerSocket {
private:
    int fd_{-1};

public:
    explicit ServerSocket(int fd = -1) noexcept : fd_{fd} {}
    ~ServerSocket() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    ServerSocket(const ServerSocket&) = delete;
    ServerSocket& operator=(const ServerSocket&) = delete;

    ServerSocket(ServerSocket&& other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }

    ServerSocket& operator=(ServerSocket&& other) noexcept {
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

[[nodiscard]] std::expected<ServerSocket, std::error_code>
create_cpp_server(uint16_t port) noexcept {
    int raw_fd = ::socket(AF_INET, SOCK_STREAM, 0);
    if (raw_fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    ServerSocket server(raw_fd);

    // Дозволити повторне використання порту при TIME_WAIT
    const int reuse = 1;
    if (::setsockopt(server.get(), SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    // Вимкнути затримку алгоритму Нейгла
    const int nodelay = 1;
    if (::setsockopt(server.get(), IPPROTO_TCP, TCP_NODELAY, &nodelay, sizeof(nodelay)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(port);

    if (::bind(server.get(), reinterpret_cast<const sockaddr*>(&addr), sizeof(addr)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    if (::listen(server.get(), 1024) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return server;
}
