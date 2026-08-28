#include <expected>
#include <string_view>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>

class UniqueSocket {
    int fd_{-1};
public:
    explicit UniqueSocket(int fd) noexcept : fd_(fd) {}
    ~UniqueSocket() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    UniqueSocket(const UniqueSocket&) = delete;
    UniqueSocket& operator=(const UniqueSocket&) = delete;
    UniqueSocket(UniqueSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    UniqueSocket& operator=(UniqueSocket&& other) noexcept {
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

[[nodiscard]] std::expected<UniqueSocket, std::error_code>
create_multicast_receiver(std::string_view mcast_addr, uint16_t port, std::string_view iface_ip) noexcept {
    int raw_fd = ::socket(AF_INET, SOCK_DGRAM, 0);
    if (raw_fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    UniqueSocket sock(raw_fd);

    int reuse = 1;
    if (::setsockopt(sock.get(), SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    sockaddr_in bind_addr{};
    bind_addr.sin_family = AF_INET;
    bind_addr.sin_port = htons(port);
    bind_addr.sin_addr.s_addr = htonl(INADDR_ANY);

    if (::bind(sock.get(), reinterpret_cast<const sockaddr*>(&bind_addr), sizeof(bind_addr)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    ip_mreq mreq{};
    if (::inet_pton(AF_INET, mcast_addr.data(), &mreq.imr_multiaddr) <= 0) {
        return std::unexpected(std::make_error_code(std::errc::invalid_argument));
    }
    if (::inet_pton(AF_INET, iface_ip.data(), &mreq.imr_interface) <= 0) {
        return std::unexpected(std::make_error_code(std::errc::invalid_argument));
    }

    if (::setsockopt(sock.get(), IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(mreq)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return sock;
}
