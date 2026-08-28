#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <cstring>
#include <system_error>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <arpa/inet.h>

class NetlinkSocket {
    int fd_{-1};
public:
    NetlinkSocket() {
        fd_ = ::socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити Netlink-сокет");
        }
    }
    ~NetlinkSocket() {
        if (fd_ >= 0) ::close(fd_);
    }
    NetlinkSocket(const NetlinkSocket&) = delete;
    NetlinkSocket& operator=(const NetlinkSocket&) = delete;

    [[nodiscard]] int get() const noexcept { return fd_; }

    void send(std::span<const std::uint8_t> buffer) const {
        struct sockaddr_nl sa{};
        sa.nl_family = AF_NETLINK;
        ssize_t sent = ::sendto(fd_, buffer.data(), buffer.size(), 0,
                                reinterpret_cast<struct sockaddr*>(&sa), sizeof(sa));
        if (sent < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка надсилання Netlink-повідомлення");
        }
    }
};

class NetlinkMessageBuilder {
    std::vector<std::uint8_t> buffer_;
public:
    NetlinkMessageBuilder(std::uint16_t type, std::uint16_t flags, std::uint32_t seq, const struct ifaddrmsg& ifa) {
        buffer_.resize(NLMSG_SPACE(sizeof(struct ifaddrmsg)), 0);
        auto* n = reinterpret_cast<struct nlmsghdr*>(buffer_.data());
        n->nlmsg_len = NLMSG_LENGTH(sizeof(struct ifaddrmsg));
        n->nlmsg_type = type;
        n->nlmsg_flags = flags;
        n->nlmsg_seq = seq;

        auto* ifa_dest = reinterpret_cast<struct ifaddrmsg*>(NLMSG_DATA(n));
        std::memcpy(ifa_dest, &ifa, sizeof(struct ifaddrmsg));
    }

    void add_attribute(std::uint16_t type, std::span<const std::uint8_t> data) {
        auto* n = reinterpret_cast<struct nlmsghdr*>(buffer_.data());
        std::size_t rta_len = RTA_LENGTH(data.size());
        std::size_t old_len = NLMSG_ALIGN(n->nlmsg_len);
        std::size_t new_len = old_len + RTA_ALIGN(rta_len);

        buffer_.resize(new_len, 0);
        n = reinterpret_cast<struct nlmsghdr*>(buffer_.data()); // Оновлюємо вказівник після resize

        auto* rta = reinterpret_cast<struct rtattr*>(buffer_.data() + old_len);
        rta->rta_type = type;
        rta->rta_len = static_cast<unsigned short>(rta_len);
        std::memcpy(RTA_DATA(rta), data.data(), data.size());

        n->nlmsg_len = static_cast<__u32>(new_len);
    }

    [[nodiscard]] std::span<const std::uint8_t> bytes() const noexcept {
        return {buffer_.data(), buffer_.size()};
    }
};

int main() {
    try {
        NetlinkSocket socket;

        struct ifaddrmsg ifa{};
        ifa.ifa_family = AF_INET;
        ifa.ifa_prefixlen = 24;
        ifa.ifa_flags = IFA_F_PERMANENT;
        ifa.ifa_scope = RT_SCOPE_UNIVERSE;
        ifa.ifa_index = 2; // ifindex цільового інтерфейсу

        NetlinkMessageBuilder builder(
            RTM_NEWADDR,
            NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK,
            1,
            ifa
        );

        struct in_addr addr{};
        if (::inet_pton(AF_INET, "192.168.10.50", &addr) != 1) {
            std::cerr << "Некоректний формат IP-адреси\n";
            return 1;
        }

        std::span<const std::uint8_t> addr_bytes(reinterpret_cast<const std::uint8_t*>(&addr), sizeof(addr));
        builder.add_attribute(IFA_LOCAL, addr_bytes);
        builder.add_attribute(IFA_ADDRESS, addr_bytes);

        socket.send(builder.bytes());
        std::cout << "Повідомлення RTM_NEWADDR успішно надіслано в ядро через C++ NetlinkSocket.\n";
    } catch (const std::exception& ex) {
        std::cerr << "Виняток: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
