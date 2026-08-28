#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <span>
#include <system_error>
#include <expected>
#include <iostream>

class SafeUdpSocket {
public:
    SafeUdpSocket() : fd_(::socket(AF_INET, SOCK_DGRAM, 0)) {
        if (fd_ < 0) throw std::system_error(errno, std::generic_category(), "socket create failed");
    }

    ~SafeUdpSocket() {
        if (fd_ >= 0) ::close(fd_);
    }

    SafeUdpSocket(const SafeUdpSocket&) = delete;
    SafeUdpSocket& operator=(const SafeUdpSocket&) = delete;
    SafeUdpSocket(SafeUdpSocket&& o) noexcept : fd_(std::exchange(o.fd_, -1)) {}

    void enable_pmtud() {
        int mode = IP_PMTUDISC_DO;
        if (::setsockopt(fd_, IPPROTO_IP, IP_MTU_DISCOVER, &mode, sizeof(mode)) < 0) {
            throw std::system_error(errno, std::generic_category(), "setsockopt IP_MTU_DISCOVER failed");
        }
    }

    [[nodiscard]] int get_current_pmtu() const {
        int pmtu = 0;
        socklen_t len = sizeof(pmtu);
        if (::getsockopt(fd_, IPPROTO_IP, IP_MTU, &pmtu, &len) < 0) {
            throw std::system_error(errno, std::generic_category(), "getsockopt IP_MTU failed");
        }
        return pmtu;
    }

    std::expected<size_t, int> send(std::span<const uint8_t> data, const sockaddr_in& dst) {
        ssize_t res = ::sendto(fd_, data.data(), data.size(), 0,
                               reinterpret_cast<const sockaddr*>(&dst), sizeof(dst));
        if (res < 0) {
            return std::unexpected(errno);
        }
        return static_cast<size_t>(res);
    }

private:
    int fd_{-1};
};
