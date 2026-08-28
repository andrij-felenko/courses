// Зчитування подій uevent через Netlink сокет у C++ (RAII, виняток замість -1)
#include <iostream>
#include <vector>
#include <string_view>
#include <system_error>
#include <cerrno>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>

class UeventSocket {
    int fd_ = -1;
public:
    UeventSocket() {
        fd_ = socket(PF_NETLINK, SOCK_RAW, NETLINK_KOBJECT_UEVENT);
        if (fd_ < 0) throw std::system_error(errno, std::generic_category());

        sockaddr_nl nls{};
        nls.nl_family = AF_NETLINK;
        nls.nl_pid = getpid();
        nls.nl_groups = -1;

        if (bind(fd_, reinterpret_cast<sockaddr*>(&nls), sizeof(nls)) < 0) {
            int err = errno;
            close(fd_);
            fd_ = -1;
            throw std::system_error(err, std::generic_category());
        }
    }

    UeventSocket(const UeventSocket&) = delete;
    UeventSocket& operator=(const UeventSocket&) = delete;

    ~UeventSocket() {
        if (fd_ >= 0) close(fd_);
    }

    void listen_events() {
        std::vector<char> buffer(4096);
        while (true) {
            ssize_t len = recv(fd_, buffer.data(), buffer.size(), 0);
            if (len > 0) {
                std::cout << "Uevent: "
                          << std::string_view(buffer.data(), static_cast<size_t>(len)) << "\n";
            }
        }
    }
};

int main() {
    try {
        UeventSocket uevent;
        uevent.listen_events();
    } catch (const std::exception& e) {
        std::cerr << "Помилка uevent сокета: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
