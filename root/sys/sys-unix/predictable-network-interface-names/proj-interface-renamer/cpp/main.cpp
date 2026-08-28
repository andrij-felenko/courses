#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <expected>
#include <cstring>
#include <system_error>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/if.h>
#include <net/if.h>

class NetlinkSocket {
public:
    NetlinkSocket() {
        fd_ = ::socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, NETLINK_ROUTE);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити сокет Netlink");
        }

        sockaddr_nl sa{};
        sa.nl_family = AF_NETLINK;

        if (::bind(fd_, reinterpret_cast<sockaddr*>(&sa), sizeof(sa)) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "Не вдалося прив'язати сокет Netlink");
        }
    }

    ~NetlinkSocket() noexcept {
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

    [[nodiscard]] int get() const noexcept { return fd_; }

private:
    int fd_{-1};
};

class InterfaceManager {
public:
    static std::expected<void, std::string> rename(std::string_view oldName, std::string_view newName) {
        if (oldName.empty() || newName.empty() || newName.length() >= IFNAMSIZ) {
            return std::unexpected("Некоректне ім'я: довжина має бути від 1 до 15 символів");
        }

        std::string oldNameStr(oldName);
        unsigned int ifindex = ::if_nametoindex(oldNameStr.c_str());
        if (ifindex == 0) {
            return std::unexpected("Інтерфейс '" + oldNameStr + "' не знайдено в системі");
        }

        try {
            NetlinkSocket sock;
            std::vector<uint8_t> buffer(4096, 0);

            auto* n = reinterpret_cast<nlmsghdr*>(buffer.data());
            n->nlmsg_len = NLMSG_LENGTH(sizeof(ifinfomsg));
            n->nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK;
            n->nlmsg_type = RTM_SETLINK;
            n->nlmsg_seq = 1001;

            auto* ifi = reinterpret_cast<ifinfomsg*>(NLMSG_DATA(n));
            ifi->ifi_family = AF_UNSPEC;
            ifi->ifi_index = static_cast<int>(ifindex);

            // Додаємо атрибут IFLA_IFNAME
            std::string newNameStr(newName);
            if (!appendAttribute(n, buffer.size(), IFLA_IFNAME, newNameStr.c_str(), newNameStr.length() + 1)) {
                return std::unexpected("Переповнення буфера при формуванні повідомлення RTNetlink");
            }

            sockaddr_nl sa{};
            sa.nl_family = AF_NETLINK;

            if (::sendto(sock.get(), n, n->nlmsg_len, 0, reinterpret_cast<sockaddr*>(&sa), sizeof(sa)) < 0) {
                return std::unexpected(std::string("Помилка надсилання в netlink: ") + std::strerror(errno));
            }

            return receiveAck(sock.get());
        } catch (const std::exception& ex) {
            return std::unexpected(ex.what());
        }
    }

private:
    static bool appendAttribute(nlmsghdr* n, size_t maxLen, uint16_t type, const void* data, size_t dataLen) {
        size_t rtaLen = RTA_LENGTH(dataLen);
        if (NLMSG_ALIGN(n->nlmsg_len) + RTA_ALIGN(rtaLen) > maxLen) {
            return false;
        }
        auto* rta = reinterpret_cast<rtattr*>(reinterpret_cast<char*>(n) + NLMSG_ALIGN(n->nlmsg_len));
        rta->rta_type = type;
        rta->rta_len = static_cast<unsigned short>(rtaLen);
        std::memcpy(RTA_DATA(rta), data, dataLen);
        n->nlmsg_len = NLMSG_ALIGN(n->nlmsg_len) + RTA_ALIGN(rtaLen);
        return true;
    }

    static std::expected<void, std::string> receiveAck(int fd) {
        std::vector<uint8_t> recvBuf(4096);
        ssize_t bytesRead = ::recv(fd, recvBuf.data(), recvBuf.size(), 0);
        if (bytesRead < 0) {
            return std::unexpected(std::string("Помилка читання відповіді ACK: ") + std::strerror(errno));
        }

        auto* h = reinterpret_cast<nlmsghdr*>(recvBuf.data());
        if (!NLMSG_OK(h, static_cast<size_t>(bytesRead))) {
            return std::unexpected("Отримано пошкоджене або неповне повідомлення Netlink");
        }

        if (h->nlmsg_type == NLMSG_ERROR) {
            auto* err = reinterpret_cast<nlmsgerr*>(NLMSG_DATA(h));
            if (h->nlmsg_len < NLMSG_LENGTH(sizeof(nlmsgerr))) {
                return std::unexpected("Усічене повідомлення про помилку від ядра");
            }
            if (err->error != 0) {
                return std::unexpected(std::string("Ядро відхилило операцію: ") + std::strerror(-err->error));
            }
        }
        return {};
    }
};

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Використання: " << argv[0] << " <старе_ім'я> <нове_ім'я>\n";
        return 1;
    }

    auto result = InterfaceManager::rename(argv[1], argv[2]);
    if (!result) {
        std::cerr << "Помилка: " << result.error() << "\n";
        return 1;
    }

    std::cout << "Інтерфейс " << argv[1] << " успішно перейменовано на " << argv[2] << "\n";
    return 0;
}
