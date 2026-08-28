#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <array>
#include <format>
#include <chrono>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <netinet/in.h>
#include <netinet/icmp6.h>
#include <arpa/inet.h>

namespace net {

/* RAII-обгортка для автоматичного керування життєвим циклом сокета */
class UniqueSocket {
public:
    UniqueSocket() noexcept : fd_(-1) {}
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

private:
    int fd_;
};

/* Отримання апаратної адреси MAC інтерфейсу */
inline std::array<uint8_t, 6> get_interface_mac(int sock_fd, std::string_view ifname) {
    struct ifreq ifr{};
    std::strncpy(ifr.ifr_name, ifname.data(), IFNAMSIZ - 1);

    if (::ioctl(sock_fd, SIOCGIFHWADDR, &ifr) < 0) {
        throw std::system_error(errno, std::generic_category(), "ioctl(SIOCGIFHWADDR) завершився помилкою");
    }

    std::array<uint8_t, 6> mac{};
    std::memcpy(mac.data(), ifr.ifr_hwaddr.sa_data, 6);
    return mac;
}

/* Формування адреси Solicited-Node Multicast */
inline in6_addr make_solicited_node_address(const in6_addr& target) noexcept {
    in6_addr solicited{};
    ::inet_pton(AF_INET6, "ff02::1:ff00:0", &solicited);
    solicited.s6_addr[13] = target.s6_addr[13];
    solicited.s6_addr[14] = target.s6_addr[14];
    solicited.s6_addr[15] = target.s6_addr[15];
    return solicited;
}

} // namespace net

int main(int argc, char* argv[]) {
    try {
        if (argc < 3) {
            std::cerr << "Використання: " << argv[0] << " <інтерфейс> <цільова-IPv6-адреса>\n";
            return 1;
        }

        const std::string_view ifname = argv[1];
        const std::string_view target_ip_str = argv[2];

        in6_addr target_ip{};
        if (::inet_pton(AF_INET6, target_ip_str.data(), &target_ip) != 1) {
            std::cerr << "Помилка: некоректний формат адреси: " << target_ip_str << "\n";
            return 1;
        }

        unsigned int ifindex = ::if_nametoindex(ifname.data());
        if (ifindex == 0) {
            std::cerr << "Помилка: мережевий інтерфейс " << ifname << " не знайдено\n";
            return 1;
        }

        net::UniqueSocket sock(::socket(AF_INET6, SOCK_RAW, IPPROTO_ICMPV6));
        if (!sock.valid()) {
            throw std::system_error(errno, std::generic_category(), "Помилка відкриття raw-сокета (потрібен sudo)");
        }

        const auto local_mac = net::get_interface_mac(sock.get(), ifname);

        int hops = 255;
        if (::setsockopt(sock.get(), IPPROTO_IPV6, IPV6_MULTICAST_HOPS, &hops, sizeof(hops)) < 0 ||
            ::setsockopt(sock.get(), IPPROTO_IPV6, IPV6_UNICAST_HOPS, &hops, sizeof(hops)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося встановити Hop Limit = 255");
        }

        struct timeval tv{ .tv_sec = 2, .tv_usec = 0 };
        if (::setsockopt(sock.get(), SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0) {
            throw std::system_error(errno, std::generic_category(), "setsockopt(SO_RCVTIMEO) failed");
        }

        if (::setsockopt(sock.get(), SOL_SOCKET, SO_BINDTODEVICE, ifname.data(), ifname.size()) < 0) {
            throw std::system_error(errno, std::generic_category(), "setsockopt(SO_BINDTODEVICE) failed");
        }

        struct ProbePacket {
            struct nd_neighbor_solicit ns_hdr;
            struct nd_opt_hdr opt_hdr;
            uint8_t mac[6];
        } __attribute__((packed));

        ProbePacket pkt{};
        pkt.ns_hdr.nd_ns_type = ND_NEIGHBOR_SOLICIT;
        pkt.ns_hdr.nd_ns_code = 0;
        pkt.ns_hdr.nd_ns_target = target_ip;
        pkt.opt_hdr.nd_opt_type = ND_OPT_SOURCE_LINKADDR;
        pkt.opt_hdr.nd_opt_len = 1;
        std::memcpy(pkt.mac, local_mac.data(), 6);

        sockaddr_in6 dst_addr{};
        dst_addr.sin6_family = AF_INET6;
        dst_addr.sin6_scope_id = ifindex;
        dst_addr.sin6_addr = net::make_solicited_node_address(target_ip);

        char solicited_buf[INET6_ADDRSTRLEN]{};
        ::inet_ntop(AF_INET6, &dst_addr.sin6_addr, solicited_buf, sizeof(solicited_buf));
        std::cout << "Надсилання Neighbor Solicitation для " << target_ip_str
                  << " на " << solicited_buf << "%" << ifname << "...\n";

        ssize_t sent = ::sendto(sock.get(), &pkt, sizeof(pkt), 0,
                                reinterpret_cast<const sockaddr*>(&dst_addr), sizeof(dst_addr));
        if (sent < 0) {
            throw std::system_error(errno, std::generic_category(), "sendto failed");
        }

        std::array<uint8_t, 1500> recv_buf{};
        while (true) {
            sockaddr_in6 src_addr{};
            socklen_t addr_len = sizeof(src_addr);
            ssize_t recvd = ::recvfrom(sock.get(), recv_buf.data(), recv_buf.size(), 0,
                                       reinterpret_cast<sockaddr*>(&src_addr), &addr_len);
            if (recvd < 0) {
                if (errno == EAGAIN || errno == EWOULDBLOCK) {
                    std::cerr << "Час очікування вичерпано: сусід не відповів на зонд.\n";
                    return 1;
                }
                throw std::system_error(errno, std::generic_category(), "recvfrom failed");
            }

            if (recvd < static_cast<ssize_t>(sizeof(struct nd_neighbor_advert))) {
                continue;
            }

            const auto* na = reinterpret_cast<const struct nd_neighbor_advert*>(recv_buf.data());
            if (na->nd_na_type != ND_NEIGHBOR_ADVERT || na->nd_na_code != 0) {
                continue;
            }

            if (std::memcmp(&na->nd_na_target, &target_ip, sizeof(in6_addr)) != 0) {
                continue;
            }

            char resp_buf[INET6_ADDRSTRLEN]{};
            ::inet_ntop(AF_INET6, &src_addr.sin6_addr, resp_buf, sizeof(resp_buf));
            std::cout << "Отримано Neighbor Advertisement від " << resp_buf << "!\n";

            std::span<const uint8_t> options(recv_buf.data() + sizeof(struct nd_neighbor_advert),
                                             recvd - sizeof(struct nd_neighbor_advert));
            bool mac_found = false;

            while (options.size() >= 8) {
                uint8_t opt_type = options[0];
                uint8_t opt_len_units = options[1];
                if (opt_len_units == 0) break;
                size_t opt_bytes = static_cast<size_t>(opt_len_units) * 8;
                if (opt_bytes > options.size()) break;

                if (opt_type == ND_OPT_TARGET_LINKADDR && opt_bytes >= 8) {
                    const auto* target_mac = options.data() + 2;
                    std::cout << std::format("Знайдено MAC-адресу: {:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}\n",
                                             target_mac[0], target_mac[1], target_mac[2],
                                             target_mac[3], target_mac[4], target_mac[5]);
                    mac_found = true;
                    break;
                }
                options = options.subspan(opt_bytes);
            }

            if (!mac_found) {
                std::cout << "У відповіді NA опція MAC-адреси відсутня.\n";
            }
            break;
        }

        return 0;
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }
}
