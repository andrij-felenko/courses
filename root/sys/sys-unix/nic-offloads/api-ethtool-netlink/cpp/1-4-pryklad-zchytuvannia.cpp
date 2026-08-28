#include <iostream>
#include <string_view>
#include <system_error>
#include <memory>
#include <cstring>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/sockios.h>
#include <linux/ethtool.h>

class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd) : fd_(fd) {}
    ~UniqueFd() { if (fd_ >= 0) ::close(fd_); }
    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;
    UniqueFd(UniqueFd&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    UniqueFd& operator=(UniqueFd&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

struct NicOffloadState {
    bool rx_checksum{false};
    bool tx_checksum{false};
    bool tso{false};
};

std::expected<NicOffloadState, std::error_code> query_nic_offloads(std::string_view ifname) {
    UniqueFd sock{::socket(AF_INET, SOCK_DGRAM, 0)};
    if (!sock.valid()) {
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

    NicOffloadState state;
    state.rx_checksum = (eval.data & ETH_FLAG_RXCSUM) != 0;
    state.tx_checksum = (eval.data & ETH_FLAG_TXCSUM) != 0;
    state.tso         = (eval.data & ETH_FLAG_TSO) != 0;

    return state;
}
