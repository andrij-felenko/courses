// macsec_control.cpp — Ідіоматична C++20-реалізація з RAII, std::span та std::expected
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <expected>
#include <span >
#include <memory>
#include <cstring>
#include <cstdint>
#include <system_error>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/if_link.h>
#include <linux/if_macsec.h>
#include <net/if.h>

namespace sysnet {

class NetlinkSocket {
    int fd_{-1};
public:
    NetlinkSocket() {
        fd_ = ::socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
    }
    ~NetlinkSocket() {
        if (fd_ >= 0) ::close(fd_);
    }
    NetlinkSocket(const NetlinkSocket&) = delete;
    NetlinkSocket& operator=(const NetlinkSocket&) = delete;
    NetlinkSocket(NetlinkSocket&& o) noexcept : fd_{o.fd_} { o.fd_ = -1; }

    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
    [[nodiscard]] int native_handle() const noexcept { return fd_; }
};

class MacsecBuilder {
    std::vector<std::uint8_t> buffer_;

    void add_attribute(std::uint16_t type, std::span<const std::uint8_t> data) {
        auto old_len = buffer_.size();
        std::size_t attr_len = RTA_LENGTH(data.size());
        buffer_.resize(old_len + RTA_ALIGN(attr_len), 0);

        auto* rta = reinterpret_cast<struct rtattr*>(buffer_.data() + old_len);
        rta->rta_type = type;
        rta->rta_len = static_cast<unsigned short>(attr_len);

        if (!data.empty()) {
            std::memcpy(RTA_DATA(rta), data.data(), data.size());
        }

        auto* nlh = reinterpret_cast<struct nlmsghdr*>(buffer_.data());
        nlh->nlmsg_len = static_cast<std::uint32_t>(buffer_.size());
    }

public:
    MacsecBuilder() {
        buffer_.resize(NLMSG_ALIGN(sizeof(struct nlmsghdr) + sizeof(struct ifinfomsg)), 0);
        auto* nlh = reinterpret_cast<struct nlmsghdr*>(buffer_.data());
        nlh->nlmsg_len = static_cast<std::uint32_t>(buffer_.size());
        nlh->nlmsg_type = RTM_NEWLINK;
        nlh->nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK;
        nlh->nlmsg_seq = 1;

        auto* ifi = reinterpret_cast<struct ifinfomsg*>(NLMSG_DATA(nlh));
        ifi->ifi_family = AF_UNSPEC;
    }

    void add_ifname(std::string_view name) {
        std::vector<std::uint8_t> data(name.begin(), name.end());
        data.push_back(0);
        add_attribute(IFLA_IFNAME, data);
    }

    void add_link(std::uint32_t parent_idx) {
        auto ptr = reinterpret_cast<const std::uint8_t*>(&parent_idx);
        add_attribute(IFLA_LINK, {ptr, sizeof(parent_idx)});
    }

    void build_macsec_payload(std::uint64_t sci, bool encrypt) {
        std::size_t linkinfo_off = buffer_.size();
        add_attribute(IFLA_LINKINFO, {});

        std::string_view kind = "macsec";
        std::vector<std::uint8_t> kind_bytes(kind.begin(), kind.end());
        kind_bytes.push_back(0);
        add_attribute(IFLA_INFO_KIND, kind_bytes);

        std::size_t infodata_off = buffer_.size();
        add_attribute(IFLA_INFO_DATA, {});

        // IFLA_MACSEC_SCI
        auto sci_ptr = reinterpret_cast<const std::uint8_t*>(&sci);
        add_attribute(IFLA_MACSEC_SCI, {sci_ptr, sizeof(sci)});

        // IFLA_MACSEC_ENCRYPT
        std::uint8_t enc = encrypt ? 1 : 0;
        add_attribute(IFLA_MACSEC_ENCRYPT, {&enc, 1});

        // Оновлюємо внутрішні довжини rta_len для вкладених атрибутів
        auto update_len = [this](std::size_t offset) {
            auto* rta = reinterpret_cast<struct rtattr*>(buffer_.data() + offset);
            rta->rta_len = static_cast<unsigned short>(buffer_.size() - offset);
        };

        update_len(infodata_off);
        update_len(linkinfo_off);
    }

    [[nodiscard]] std::span<const std::uint8_t> data() const noexcept {
        return buffer_;
    }
};

[[nodiscard]] std::expected<void, std::string> create_macsec(std::string_view ifname,
                                                              std::string_view parent_ifname,
                                                              std::uint64_t sci) {
    NetlinkSocket nl_sock;
    if (!nl_sock.valid()) {
        return std::unexpected("Не вдалося створити сокет AF_NETLINK");
    }

    unsigned int parent_idx = ::if_nametoindex(parent_ifname.data());
    if (parent_idx == 0) {
        return std::unexpected("Базовий пристрій не знайдено");
    }

    MacsecBuilder builder;
    builder.add_ifname(ifname);
    builder.add_link(parent_idx);
    builder.build_macsec_payload(sci, true);

    auto msg = builder.data();
    struct sockaddr_nl sa{};
    sa.nl_family = AF_NETLINK;

    if (::sendto(nl_sock.native_handle(), msg.data(), msg.size(), 0,
                 reinterpret_cast<struct sockaddr*>(&sa), sizeof(sa)) < 0) {
        return std::unexpected(std::strerror(errno));
    }

    std::vector<std::uint8_t> rx_buf(4096);
    ssize_t len = ::recv(nl_sock.native_handle(), rx_buf.data(), rx_buf.size(), 0);
    if (len < 0) {
        return std::unexpected("Помилка читання з Netlink сокета");
    }

    auto* nlh = reinterpret_cast<struct nlmsghdr*>(rx_buf.data());
    if (nlh->nlmsg_type == NLMSG_ERROR) {
        auto* err = reinterpret_cast<struct nlmsgerr*>(NLMSG_DATA(nlh));
        if (err->error != 0) {
            return std::unexpected(std::strerror(-err->error));
        }
    }

    return {};
}

} // namespace sysnet

int main() {
    constexpr std::uint64_t sci = 0x0011223344550001ULL;
    auto result = sysnet::create_macsec("macsec0", "eth0", sci);
    
    if (!result) {
        std::cerr << "Помилка конфігурації MACsec: " << result.error() << '\n';
        return 1;
    }

    std::cout << "Інтерфейс macsec0 успішно сконфігуровано через C++ Netlink API.\n";
    return 0;
}
