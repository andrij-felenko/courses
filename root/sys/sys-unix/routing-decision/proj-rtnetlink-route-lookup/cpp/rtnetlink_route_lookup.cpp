/*
 * rtnetlink_route_lookup.cpp
 * Ідіоматична реалізація мовою C++20 з використанням RAII, std::span та std::expected.
 */

#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <expected>
#include <system_error>
#include <memory>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <linux/rtnetlink.h>

namespace net {

// RAII обгортка навколо Netlink сокета
class NetlinkSocket {
public:
    explicit NetlinkSocket(int protocol) {
        fd_ = ::socket(AF_NETLINK, SOCK_RAW, protocol);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося створити AF_NETLINK сокет");
        }
    }

    ~NetlinkSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    NetlinkSocket(const NetlinkSocket&) = delete;
    NetlinkSocket& operator=(const NetlinkSocket&) = delete;

    NetlinkSocket(NetlinkSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    NetlinkSocket& operator=(NetlinkSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    void bind(uint32_t groups) {
        sockaddr_nl sa{};
        sa.nl_family = AF_NETLINK;
        sa.nl_groups = groups;

        if (::bind(fd_, reinterpret_cast<sockaddr*>(&sa), sizeof(sa)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка bind() для Netlink");
        }
    }

    void send(std::span<const uint8_t> data) const {
        if (::send(fd_, data.data(), data.size(), 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка відправки в Netlink");
        }
    }

    ssize_t receive(std::span<uint8_t> buffer) const {
        ssize_t ret = ::recv(fd_, buffer.data(), buffer.size(), 0);
        if (ret < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка читання з Netlink");
        }
        return ret;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }

private:
    int fd_{-1};
};

struct RouteInfo {
    std::string destination;
    uint8_t prefix_len{0};
    std::string gateway;
    std::string preferred_src;
    std::string interface_name;
    uint32_t interface_index{0};
    uint16_t msg_type{0};
};

// Парсинг атрибутів повідомлення RTM_NEWROUTE
inline RouteInfo parse_rtmsg(const nlmsghdr* nlh) {
    RouteInfo info{};
    info.msg_type = nlh->nlmsg_type;

    const auto* rt = reinterpret_cast<const rtmsg*>(NLMSG_DATA(nlh));
    info.prefix_len = rt->rtm_dst_len;

    const auto* rta = reinterpret_cast<const rtattr*>(RTM_RTA(rt));
    int rtl = RTM_PAYLOAD(nlh);

    char addr_buf[INET_ADDRSTRLEN]{0};

    for (; RTA_OK(rta, rtl); rta = RTA_NEXT(rta, rtl)) {
        switch (rta->rta_type) {
            case RTA_DST:
                ::inet_ntop(AF_INET, RTA_DATA(rta), addr_buf, sizeof(addr_buf));
                info.destination = addr_buf;
                break;
            case RTA_GATEWAY:
                ::inet_ntop(AF_INET, RTA_DATA(rta), addr_buf, sizeof(addr_buf));
                info.gateway = addr_buf;
                break;
            case RTA_PREFSRC:
                ::inet_ntop(AF_INET, RTA_DATA(rta), addr_buf, sizeof(addr_buf));
                info.preferred_src = addr_buf;
                break;
            case RTA_OIF:
                info.interface_index = *reinterpret_cast<const uint32_t*>(RTA_DATA(rta));
                break;
        }
    }

    if (info.destination.empty()) info.destination = "default";
    if (info.gateway.empty()) info.gateway = "none";
    if (info.preferred_src.empty()) info.preferred_src = "none";

    if (info.interface_index > 0) {
        char ifbuf[IF_NAMESIZE]{0};
        if (::if_indextoname(info.interface_index, ifbuf)) {
            info.interface_name = ifbuf;
        } else {
            info.interface_name = "unknown";
        }
    }

    return info;
}

} // namespace net

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <Destination IPv4>\n";
        return EXIT_FAILURE;
    }

    in_addr dst_addr{};
    if (::inet_pton(AF_INET, argv[1], &dst_addr) <= 0) {
        std::cerr << "Некоректна IP-адреса: " << argv[1] << "\n";
        return EXIT_FAILURE;
    }

    try {
        net::NetlinkSocket sock(NETLINK_ROUTE);
        sock.bind(RTMGRP_IPV4_ROUTE);

        // Будуємо повідомлення RTM_GETROUTE
        std::vector<uint8_t> request_buf(NLMSG_SPACE(sizeof(rtmsg)) + RTA_SPACE(sizeof(in_addr)));
        
        auto* nlh = reinterpret_cast<nlmsghdr*>(request_buf.data());
        nlh->nlmsg_len = NLMSG_LENGTH(sizeof(rtmsg));
        nlh->nlmsg_flags = NLM_F_REQUEST;
        nlh->nlmsg_type = RTM_GETROUTE;

        auto* rt = reinterpret_cast<rtmsg*>(NLMSG_DATA(nlh));
        rt->rtm_family = AF_INET;
        rt->rtm_dst_len = 32;

        // Додаємо атрибут RTA_DST
        auto* rta = reinterpret_cast<rtattr*>(reinterpret_cast<char*>(nlh) + NLMSG_ALIGN(nlh->nlmsg_len));
        rta->rta_type = RTA_DST;
        rta->rta_len = RTA_LENGTH(sizeof(in_addr));
        std::memcpy(RTA_DATA(rta), &dst_addr, sizeof(in_addr));
        nlh->nlmsg_len = NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(rta->rta_len);

        sock.send(request_buf);
        std::cout << "Надіслано запит RTM_GETROUTE для IP: " << argv[1] << "\n";

        std::vector<uint8_t> rx_buffer(8192);
        while (true) {
            ssize_t len = sock.receive(rx_buffer);
            const auto* rx_nlh = reinterpret_cast<const nlmsghdr*>(rx_buffer.data());

            for (; NLMSG_OK(rx_nlh, len); rx_nlh = NLMSG_NEXT(rx_nlh, len)) {
                if (rx_nlh->nlmsg_type == NLMSG_DONE) break;
                if (rx_nlh->nlmsg_type == NLMSG_ERROR) {
                    std::cerr << "Помилка ядра Netlink\n";
                    break;
                }
                if (rx_nlh->nlmsg_type == RTM_NEWROUTE || rx_nlh->nlmsg_type == RTM_DELROUTE) {
                    auto info = net::parse_rtmsg(rx_nlh);
                    std::cout << (info.msg_type == RTM_NEWROUTE ? "[NEW] " : "[DEL] ")
                              << "Призначення: " << info.destination << "/" << static_cast<int>(info.prefix_len)
                              << " | Шлюз: " << info.gateway
                              << " | Джерело: " << info.preferred_src
                              << " | Інтерфейс: " << info.interface_name << " (" << info.interface_index << ")\n";
                }
            }
        }
    } catch (const std::exception& ex) {
        std::cerr << "Виключна ситуація: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
