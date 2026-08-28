// C++20 implementation: querying interface state using RAII and std::span
#include <iostream>
#include <vector>
#include <string_view>
#include <span>
#include <memory>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <net/if.h>

class NetlinkSocket {
    int fd_{-1};
public:
    NetlinkSocket() {
        fd_ = ::socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to open AF_NETLINK socket");
        }
    }
    ~NetlinkSocket() {
        if (fd_ >= 0) ::close(fd_);
    }
    NetlinkSocket(const NetlinkSocket&) = delete;
    NetlinkSocket& operator=(const NetlinkSocket&) = delete;
    NetlinkSocket(NetlinkSocket&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    NetlinkSocket& operator=(NetlinkSocket&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
};

struct InterfaceInfo {
    int index{0};
    std::string name;
    uint32_t mtu{0};
    bool is_up{false};
    bool is_running{false};
    uint8_t operstate{0};
};

std::vector<InterfaceInfo> fetch_interfaces() {
    NetlinkSocket sock;

    struct alignas(NLMSG_ALIGNTO) DumpRequest {
        nlmsghdr nlh;
        ifinfomsg ifm;
    } req{};

    req.nlh.nlmsg_len = NLMSG_LENGTH(sizeof(ifinfomsg));
    req.nlh.nlmsg_type = RTM_GETLINK;
    req.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_DUMP;
    req.nlh.nlmsg_seq = 1;
    req.ifm.ifi_family = AF_UNSPEC;

    if (::send(sock.get(), &req, req.nlh.nlmsg_len, 0) < 0) {
        throw std::system_error(errno, std::generic_category(), "Failed to send RTNETLINK dump request");
    }

    std::vector<uint8_t> buffer(16384);
    ssize_t bytes_read = ::recv(sock.get(), buffer.data(), buffer.size(), 0);
    if (bytes_read < 0) {
        throw std::system_error(errno, std::generic_category(), "Failed to receive RTNETLINK response");
    }

    std::vector<InterfaceInfo> result;
    auto msg_len = static_cast<size_t>(bytes_read);
    auto* nlh = reinterpret_cast<nlmsghdr*>(buffer.data());

    for (; NLMSG_OK(nlh, msg_len); nlh = NLMSG_NEXT(nlh, msg_len)) {
        if (nlh->nlmsg_type == NLMSG_DONE) break;
        if (nlh->nlmsg_type == NLMSG_ERROR) {
            throw std::runtime_error("Netlink returned error header");
        }

        if (nlh->nlmsg_type == RTM_NEWLINK) {
            auto* ifi = static_cast<ifinfomsg*>(NLMSG_DATA(nlh));
            InterfaceInfo info{};
            info.index = ifi->ifi_index;
            info.is_up = (ifi->ifi_flags & IFF_UP) != 0;
            info.is_running = (ifi->ifi_flags & IFF_RUNNING) != 0;

            auto rta_len = static_cast<int>(nlh->nlmsg_len - NLMSG_SPACE(sizeof(*ifi)));
            auto* rta = IFLA_RTA(ifi);

            std::vector<rtattr*> tb(IFLA_MAX + 1, nullptr);
            while (RTA_OK(rta, rta_len)) {
                if (rta->rta_type <= IFLA_MAX) {
                    tb[rta->rta_type] = rta;
                }
                rta = RTA_NEXT(rta, rta_len);
            }

            if (tb[IFLA_IFNAME]) {
                info.name = static_cast<const char*>(RTA_DATA(tb[IFLA_IFNAME]));
            }
            if (tb[IFLA_MTU]) {
                info.mtu = *static_cast<uint32_t*>(RTA_DATA(tb[IFLA_MTU]));
            }
            if (tb[IFLA_OPERSTATE]) {
                info.operstate = *static_cast<uint8_t*>(RTA_DATA(tb[IFLA_OPERSTATE]));
            }

            result.push_back(std::move(info));
        }
    }

    return result;
}

int main() {
    try {
        auto interfaces = fetch_interfaces();
        for (const auto& dev : interfaces) {
            std::cout << "Dev [" << dev.index << "]: " << dev.name
                      << " MTU=" << dev.mtu
                      << " UP=" << (dev.is_up ? "1" : "0")
                      << " RUNNING=" << (dev.is_running ? "1" : "0")
                      << " OperState=" << static_cast<int>(dev.operstate) << "\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "Fatal error: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
