#include <iostream>
#include <string_view>
#include <array>
#include <system_error>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

class SocketWrapper {
    int fd_{-1};
public:
    explicit SocketWrapper(int fd) : fd_(fd) {}
    ~SocketWrapper() { if (fd_ >= 0) ::close(fd_); }
    [[nodiscard]] int get() const noexcept { return fd_; }
};

int main() {
    int raw_fd = ::socket(AF_INET, SOCK_STREAM, 0);
    if (raw_fd < 0) {
        throw std::system_error(errno, std::generic_category(), "socket failed");
    }
    SocketWrapper client_sock(raw_fd);

    sockaddr_in serv_addr{};
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(8080);

    if (::inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr) <= 0) {
        throw std::system_error(errno, std::generic_category(), "invalid IP address");
    }

    if (::connect(client_sock.get(), reinterpret_cast<sockaddr*>(&serv_addr), sizeof(serv_addr)) < 0) {
        throw std::system_error(errno, std::generic_category(), "connect failed");
    }

    std::cout << "Connected to 127.0.0.1:8080\n";

    constexpr std::string_view msg = "Hello from C++20 Socket Client!";
    if (::write(client_sock.get(), msg.data(), msg.size()) < 0) {
        throw std::system_error(errno, std::generic_category(), "write failed");
    }

    std::array<char, 1024> response{};
    ssize_t bytes_read = ::read(client_sock.get(), response.data(), response.size() - 1);
    if (bytes_read > 0) {
        response[bytes_read] = '\0';
        std::cout << "Received echo: " << response.data() << "\n";
    }

    return 0;
}
