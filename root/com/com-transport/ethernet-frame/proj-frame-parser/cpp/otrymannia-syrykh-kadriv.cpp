#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netpacket/packet.h>
#include <net/ethernet.h>
#include <net/if.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>
#include <string_view>
#include <expected>

namespace net {

class raw_socket {
    int fd_{-1};

public:
    raw_socket() = default;
    explicit raw_socket(int fd) noexcept : fd_(fd) {}

    ~raw_socket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    raw_socket(const raw_socket&) = delete;
    raw_socket& operator=(const raw_socket&) = delete;

    raw_socket(raw_socket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    raw_socket& operator=(raw_socket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }
    [[nodiscard]] bool is_open() const noexcept { return fd_ >= 0; }

    static std::expected<raw_socket, int> open(std::string_view ifname) {
        int sock = ::socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
        if (sock < 0)
            return std::unexpected(-1);

        struct ifreq ifr{};
        std::strncpy(ifr.ifr_name, ifname.data(), sizeof(ifr.ifr_name) - 1);
        if (::ioctl(sock, SIOCGIFINDEX, &ifr) < 0) {
            ::close(sock);
            return std::unexpected(-2);
        }

        struct sockaddr_ll sll{};
        sll.sll_family = AF_PACKET;
        sll.sll_ifindex = ifr.ifr_ifindex;
        sll.sll_protocol = htons(ETH_P_ALL);

        if (::bind(sock, reinterpret_cast<struct sockaddr*>(&sll), sizeof(sll)) < 0) {
            ::close(sock);
            return std::unexpected(-3);
        }

        return raw_socket(sock);
    }
};

} // namespace net
