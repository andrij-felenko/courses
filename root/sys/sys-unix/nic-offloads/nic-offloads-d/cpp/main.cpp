#include <iostream>
#include <string_view>
#include <system_error>
#include <expected>
#include <cstring>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/sockios.h>
#include <linux/ethtool.h>

class SocketHandle {
    int fd_{-1};
public:
    explicit SocketHandle(int fd) : fd_(fd) {}
    ~SocketHandle() { if (fd_ >= 0) ::close(fd_); }
    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;
    SocketHandle(SocketHandle&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    SocketHandle& operator=(SocketHandle&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
};

struct OffloadStatus {
    bool rx_csum{false};
    bool tx_csum{false};
    bool tso{false};
};

std::expected<OffloadStatus, std::error_code> get_nic_offloads(std::string_view ifname) {
    SocketHandle sock{::socket(AF_INET, SOCK_DGRAM, 0)};
    if (sock.get() < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    ::ethtool_value eval{};
    eval.cmd = ETHTOOL_GFLAGS;

    ::ifreq ifr{};
    std::strncpy(ifr.ifr_name, ifname.data(), std::min(ifname.size(), sizeof(ifr.ifr_name) - 1));
    ifr.ifr_data = reinterpret_cast<caddr_t>(&eval);

    if (::ioctl(sock.get(), SIOCETHTOOL, &ifr) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    OffloadStatus st;
    st.rx_csum = (eval.data & ETH_FLAG_RXCSUM) != 0;
    st.tx_csum = (eval.data & ETH_FLAG_TXCSUM) != 0;
    st.tso     = (eval.data & ETH_FLAG_TSO) != 0;

    return st;
}
