#include <iostream>
#include <vector>
#include <string_view>
#include <expected>
#include <cstring>
#include <system_error>
#include <unistd.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/if_link.h>

namespace netlink {

// RAII обгортка для управління ресурсами файлового дескриптора сокета
class SocketFd {
    int fd_{-1};
public:
    explicit SocketFd(int fd) : fd_(fd) {}
    ~SocketFd() {
        if (fd_ >= 0) ::close(fd_);
    }
    SocketFd(const SocketFd&) = delete;
    SocketFd& operator=(const SocketFd&) = delete;
    SocketFd(SocketFd&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    SocketFd& operator=(SocketFd&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
};

// Будівельник Netlink повідомлень із безпечною роботою з пам'яттю
class MacvlanBuilder {
    std::vector<uint8_t> buffer_;

    void add_attr(uint16_t type, const void* data, size_t len) {
        size_t attr_len = RTA_LENGTH(len);
        size_t old_size = buffer_.size();
        buffer_.resize(NLMSG_ALIGN(old_size) + RTA_ALIGN(attr_len), 0);

        auto* rta = reinterpret_cast<struct rtattr*>(buffer_.data() + NLMSG_ALIGN(old_size));
        rta->rta_type = type;
        rta->rta_len = static_cast<unsigned short>(attr_len);

        if (len > 0 && data) {
            std::memcpy(RTA_DATA(rta), data, len);
        }

        auto* nlh = reinterpret_cast<struct nlmsghdr*>(buffer_.data());
        nlh->nlmsg_len = static_cast<uint32_t>(buffer_.size());
    }

public:
    MacvlanBuilder() {
        buffer_.resize(NLMSG_LENGTH(sizeof(struct ifinfomsg)), 0);
        auto* nlh = reinterpret_cast<struct nlmsghdr*>(buffer_.data());
        nlh->nlmsg_len = sizeof(struct nlmsghdr) + sizeof(struct ifinfomsg);
        nlh->nlmsg_type = RTM_NEWLINK;
        nlh->nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK | NLM_F_CREATE | NLM_F_EXCL;
        nlh->nlmsg_seq = 1;

        auto* ifi = reinterpret_cast<struct ifinfomsg*>(NLMSG_DATA(nlh));
        ifi->ifi_family = AF_UNSPEC;
    }

    std::expected<void, std::string> create(std::string_view parent_if, std::string_view macvlan_if, uint32_t mode) {
        unsigned int parent_idx = ::if_nametoindex(parent_if.data());
        if (parent_idx == 0) {
            return std::unexpected("Невідомий батьківський інтерфейс: " + std::string(parent_if));
        }

        add_attr(IFLA_IFNAME, macvlan_if.data(), macvlan_if.size() + 1);
        add_attr(IFLA_LINK, &parent_idx, sizeof(parent_idx));

        size_t linkinfo_off = buffer_.size();
        add_attr(IFLA_LINKINFO, nullptr, 0);

        std::string_view kind = "macvlan";
        add_attr(IFLA_INFO_KIND, kind.data(), kind.size() + 1);

        size_t infodata_off = buffer_.size();
        add_attr(IFLA_INFO_DATA, nullptr, 0);

        add_attr(IFLA_MACVLAN_MODE, &mode, sizeof(mode));

        // Фіксуємо підсумкові довжини вкладених rtattr
        auto* infodata = reinterpret_cast<struct rtattr*>(buffer_.data() + infodata_off);
        infodata->rta_len = static_cast<unsigned short>(buffer_.size() - infodata_off);

        auto* linkinfo = reinterpret_cast<struct rtattr*>(buffer_.data() + linkinfo_off);
        linkinfo->rta_len = static_cast<unsigned short>(buffer_.size() - linkinfo_off);

        int sock_raw = ::socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
        if (sock_raw < 0) {
            return std::unexpected("Помилка створення сокета AF_NETLINK: " + std::string(strerror(errno)));
        }
        SocketFd sock(sock_raw);

        struct sockaddr_nl sa{};
        sa.nl_family = AF_NETLINK;

        if (::sendto(sock.get(), buffer_.data(), buffer_.size(), 0,
                     reinterpret_cast<struct sockaddr*>(&sa), sizeof(sa)) < 0) {
            return std::unexpected("Помилка sendto у Netlink: " + std::string(strerror(errno)));
        }

        std::vector<uint8_t> ack_buf(4096);
        ssize_t ret = ::recv(sock.get(), ack_buf.data(), ack_buf.size(), 0);
        if (ret < 0) {
            return std::unexpected("Помилка прийому ACK від ядра: " + std::string(strerror(errno)));
        }

        auto* ack_nlh = reinterpret_cast<struct nlmsghdr*>(ack_buf.data());
        if (ack_nlh->nlmsg_type == NLMSG_ERROR) {
            auto* err = reinterpret_cast<struct nlmsgerr*>(NLMSG_DATA(ack_nlh));
            if (err->error != 0) {
                return std::unexpected("Помилка Netlink від ядра: " + std::string(strerror(-err->error)));
            }
        }

        return {};
    }
};

} // namespace netlink

int main() {
    netlink::MacvlanBuilder builder;
    // MACVLAN_MODE_BRIDGE = 2
    auto res = builder.create("eth0", "mvlan0", 2);
    if (!res) {
        std::cerr << "Помилка: " << res.error() << std::endl;
        return 1;
    }
    std::cout << "Успішно створено Macvlan через C++20 RTNetlink API!" << std::endl;
    return 0;
}
