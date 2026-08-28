#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <memory>
#include <span>
#include <string>
#include <string_view>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sched.h>
#include <sys/socket.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <linux/rtnetlink.h>
#include <linux/veth.h>
#include <net/if.h>

namespace netns {

// RAII обгортка для безпечного управління файловими дескрипторами
class ScopedFd {
    int fd_{-1};
public:
    explicit ScopedFd(int fd = -1) noexcept : fd_(fd) {}
    ~ScopedFd() { reset(); }

    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;

    ScopedFd(ScopedFd&& other) noexcept : fd_(other.release()) {}
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int temp = fd_;
        fd_ = -1;
        return temp;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

class NetnsManager {
    static constexpr std::string_view kNetnsPath = "/var/run/netns/demo_cpp_ns";

public:
    static void setup_isolated_veth(std::string_view host_if, std::string_view ns_if) {
        ScopedFd orig_netns{::open("/proc/self/ns/net", O_RDONLY | O_CLOEXEC)};
        if (!orig_netns.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити /proc/self/ns/net");
        }

        ::mkdir("/var/run/netns", 0755);
        ScopedFd touch_fd{::open(kNetnsPath.data(), O_CREAT | O_RDWR | O_EXCL | O_CLOEXEC, 0644)};

        if (::unshare(CLONE_NEWNET) != 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка unshare(CLONE_NEWNET)");
        }

        if (::mount("/proc/self/ns/net", kNetnsPath.data(), nullptr, MS_BIND, nullptr) != 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка bind mount netns");
        }

        ScopedFd target_netns{::open(kNetnsPath.data(), O_RDONLY | O_CLOEXEC)};
        if (!target_netns.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити створений netns");
        }

        // Повернення контексту до початкового мережевого простору
        if (::setns(orig_netns.get(), CLONE_NEWNET) != 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка повернення setns()");
        }

        ScopedFd nl_socket{::socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, NETLINK_ROUTE)};
        if (!nl_socket.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити Netlink сокет");
        }

        send_rtnetlink_veth_create(nl_socket.get(), host_if, ns_if, target_netns.get());
        std::cout << "[C++ RAII] Створено простір " << kNetnsPath
                  << ", надіслано запит на пару " << host_if << " <-> " << ns_if
                  << " (підтвердження ядра розбирається у §5)\n";
    }

private:
    static void send_rtnetlink_veth_create(int socket_fd, std::string_view host_if, 
                                           std::string_view ns_if, int target_ns_fd) {
        std::array<char, 1024> buffer{};
        auto* nlh = reinterpret_cast<struct nlmsghdr*>(buffer.data());

        nlh->nlmsg_len = NLMSG_LENGTH(sizeof(struct ifinfomsg));
        nlh->nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK;
        nlh->nlmsg_type = RTM_NEWLINK;

        auto append_attr = [&](uint16_t type, std::span<const char> data, size_t base_offset) -> size_t {
            auto* rta = reinterpret_cast<struct rtattr*>(buffer.data() + base_offset);
            rta->rta_type = type;
            rta->rta_len = RTA_LENGTH(data.size());
            std::copy(data.begin(), data.end(), static_cast<char*>(RTA_DATA(rta)));
            return RTA_ALIGN(rta->rta_len);
        };
        // Рядок кладеться разом із термінальним нулем; std::string дає власний
        // буфер, тож span не виходить за межі чужої пам'яті (на відміну від
        // string_view, у якого нуля за кінцем може й не бути)
        auto append_str = [&](uint16_t type, std::string_view value, size_t base_offset) -> size_t {
            const std::string owned{value};
            return append_attr(type, {owned.c_str(), owned.size() + 1}, base_offset);
        };
        // Заголовок вкладеного атрибута: довжину допишемо, коли буде відомий вміст
        auto open_nested = [&](uint16_t type, size_t base_offset) -> size_t {
            auto* rta = reinterpret_cast<struct rtattr*>(buffer.data() + base_offset);
            rta->rta_type = type;
            rta->rta_len = RTA_LENGTH(0);
            return base_offset;
        };
        auto close_nested = [&](size_t nested_offset, size_t end_offset) {
            auto* rta = reinterpret_cast<struct rtattr*>(buffer.data() + nested_offset);
            rta->rta_len = static_cast<unsigned short>(end_offset - nested_offset);
        };

        size_t offset = nlh->nlmsg_len;

        // IFLA_IFNAME — ім'я хостового кінця пари
        offset += append_str(IFLA_IFNAME, host_if, offset);

        // IFLA_LINKINFO { INFO_KIND="veth", INFO_DATA { VETH_INFO_PEER {…} } }
        const size_t linkinfo = open_nested(IFLA_LINKINFO, offset);
        offset += RTA_LENGTH(0);
        offset += append_str(IFLA_INFO_KIND, "veth", offset);

        const size_t info_data = open_nested(IFLA_INFO_DATA, offset);
        offset += RTA_LENGTH(0);

        const size_t peer = open_nested(VETH_INFO_PEER, offset);
        offset += RTA_LENGTH(sizeof(struct ifinfomsg));   // нульовий ifinfomsg парного кінця
        offset += append_str(IFLA_IFNAME, ns_if, offset);
        // Дескриптор цільового простору: peer народжується вже всередині нього
        const auto ns_fd_bytes = std::bit_cast<std::array<char, sizeof(int)>>(target_ns_fd);
        offset += append_attr(IFLA_NET_NS_FD, ns_fd_bytes, offset);

        close_nested(peer, offset);
        close_nested(info_data, offset);
        close_nested(linkinfo, offset);
        nlh->nlmsg_len = static_cast<std::uint32_t>(offset);

        // Відправка запиту у ядро
        sockaddr_nl sa{.nl_family = AF_NETLINK};
        if (::sendto(socket_fd, buffer.data(), nlh->nlmsg_len, 0, 
                     reinterpret_cast<struct sockaddr*>(&sa), sizeof(sa)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відправити Netlink повідомлення");
        }
    }
};

} // namespace netns

int main() {
    try {
        netns::NetnsManager::setup_isolated_veth("veth-host-cpp", "veth-ns-cpp");
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
