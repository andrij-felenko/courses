#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <span>
#include <expected>
#include <system_error>
#include <memory>
#include <cstring>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

class SocketHandle {
private:
    int fd_{-1};

public:
    explicit SocketHandle(int fd = -1) noexcept : fd_{fd} {}
    ~SocketHandle() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;

    SocketHandle(SocketHandle&& other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }

    SocketHandle& operator=(SocketHandle&& other) noexcept {
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

    [[nodiscard]] std::expected<void, std::error_code> shutdown_write() const noexcept {
        if (::shutdown(fd_, SHUT_WR) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }
};

[[nodiscard]] std::expected<void, std::error_code>
run_cpp_client(std::string_view server_ip, uint16_t port) noexcept {
    int raw_fd = ::socket(AF_INET, SOCK_STREAM, 0);
    if (raw_fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    SocketHandle sock(raw_fd);

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    if (::inet_pton(AF_INET, server_ip.data(), &addr.sin_addr) <= 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    if (::connect(sock.get(), reinterpret_cast<const sockaddr*>(&addr), sizeof(addr)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    // 1. Потокова передача повідомлень застосунку
    const std::array<std::string_view, 3> messages{
        "LOG_ENTRY: 2026-08-18 10:00:01 Node initialized\n",
        "LOG_ENTRY: 2026-08-18 10:00:02 Subsystems verified\n",
        "LOG_ENTRY: 2026-08-18 10:00:03 Telemetry stream active\n"
    };

    for (const auto& msg : messages) {
        ssize_t sent = ::write(sock.get(), msg.data(), msg.size());
        if (sent < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
    }

    // 2. Напівзакриття каналу передачі (відправка FIN)
    auto shut_res = sock.shutdown_write();
    if (!shut_res) {
        return std::unexpected(shut_res.error());
    }

    // 3. Отримання фінального звіту сервера
    std::array<char, 4096> buffer{};
    ssize_t bytes_read = 0;
    while ((bytes_read = ::read(sock.get(), buffer.data(), buffer.size())) > 0) {
        std::string_view report(buffer.data(), static_cast<size_t>(bytes_read));
        std::cout << "[C++ Клієнт] Звіт сервера: " << report;
    }

    if (bytes_read < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return {};
}

[[nodiscard]] std::expected<void, std::error_code>
run_cpp_server(uint16_t port) noexcept {
    int listen_raw = ::socket(AF_INET, SOCK_STREAM, 0);
    if (listen_raw < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    SocketHandle listen_sock(listen_raw);

    const int reuse = 1;
    ::setsockopt(listen_sock.get(), SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);

    if (::bind(listen_sock.get(), reinterpret_cast<const sockaddr*>(&addr), sizeof(addr)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    if (::listen(listen_sock.get(), 16) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    int client_raw = ::accept(listen_sock.get(), nullptr, nullptr);
    if (client_raw < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    SocketHandle client_sock(client_raw);

    std::array<char, 4096> buffer{};
    size_t total_bytes = 0;
    size_t line_count = 0;
    ssize_t bytes_read = 0;

    // Вичитка вхідного потоку до надходження FIN (EOF, read повертає 0)
    while ((bytes_read = ::read(client_sock.get(), buffer.data(), buffer.size())) > 0) {
        total_bytes += static_cast<size_t>(bytes_read);
        for (ssize_t i = 0; i < bytes_read; ++i) {
            if (buffer[static_cast<size_t>(i)] == '\n') {
                line_count++;
            }
        }
    }

    if (bytes_read < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    // Формування підсумкового звіту
    std::string report = "REPORT: OK. Прийнято " + std::to_string(total_bytes) +
                         " байтів, рядків: " + std::to_string(line_count) + ".\n";
    ssize_t sent = ::write(client_sock.get(), report.data(), report.size());
    if (sent < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return {};
}
