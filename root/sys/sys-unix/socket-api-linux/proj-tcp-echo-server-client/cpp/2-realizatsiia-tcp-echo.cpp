#include <iostream>
#include <string_view>
#include <vector>
#include <system_error>
#include <memory>
#include <array>
#include <csignal>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

class Socket {
private:
    int fd_{-1};

public:
    explicit Socket(int fd) : fd_(fd) {}
    ~Socket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    Socket(const Socket&) = delete;
    Socket& operator=(const Socket&) = delete;

    Socket(Socket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    Socket& operator=(Socket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

static volatile std::sig_atomic_t g_running = 1;

void signal_handler(int) {
    g_running = 0;
}

int main() {
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    int raw_fd = ::socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (raw_fd < 0) {
        throw std::system_error(errno, std::generic_category(), "socket creation failed");
    }
    Socket server_sock(raw_fd);

    int optval = 1;
    if (::setsockopt(server_sock.get(), SOL_SOCKET, SO_REUSEADDR, &optval, sizeof(optval)) < 0) {
        throw std::system_error(errno, std::generic_category(), "setsockopt SO_REUSEADDR failed");
    }

    sockaddr_in server_addr{};
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(8080);

    if (::bind(server_sock.get(), reinterpret_cast<sockaddr*>(&server_addr), sizeof(server_addr)) < 0) {
        throw std::system_error(errno, std::generic_category(), "bind failed");
    }

    if (::listen(server_sock.get(), 128) < 0) {
        throw std::system_error(errno, std::generic_category(), "listen failed");
    }

    std::cout << "C++ Idiomatic TCP Echo Server listening on port 8080...\n";

    while (g_running) {
        sockaddr_in client_addr{};
        socklen_t client_len = sizeof(client_addr);

        int client_raw_fd = ::accept4(server_sock.get(), reinterpret_cast<sockaddr*>(&client_addr),
                                      &client_len, SOCK_CLOEXEC);
        if (client_raw_fd < 0) {
            if (errno == EINTR) continue;
            break;
        }

        Socket client_sock(client_raw_fd);
        std::array<char, INET_ADDRSTRLEN> ip_str{};
        ::inet_ntop(AF_INET, &client_addr.sin_addr, ip_str.data(), ip_str.size());

        std::cout << "Client connected from " << ip_str.data() << ":" << ntohs(client_addr.sin_port)
                  << " (RAII fd=" << client_sock.get() << ")\n";

        std::array<char, 1024> buffer{};
        ssize_t bytes_read = 0;
        while ((bytes_read = ::read(client_sock.get(), buffer.data(), buffer.size())) > 0) {
            ssize_t bytes_written = 0;
            while (bytes_written < bytes_read) {
                ssize_t res = ::write(client_sock.get(), buffer.data() + bytes_written,
                                      static_cast<size_t>(bytes_read - bytes_written));
                if (res <= 0) {
                    if (res < 0 && errno == EINTR) continue;
                    break;
                }
                bytes_written += res;
            }
        }

        std::cout << "Closing client socket via RAII destructor\n";
    }

    std::cout << "Server graceful shutdown complete.\n";
    return 0;
}
