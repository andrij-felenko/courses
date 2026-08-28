// devtmpfs_inspector.cpp — Перехоплення uevent та перевірка вузлів у devtmpfs (C++)
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <filesystem>
#include <system_error>
#include <thread>
#include <chrono>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <linux/netlink.h>

namespace fs = std::filesystem;

class NetlinkSocket {
    int fd_ = -1;

public:
    explicit NetlinkSocket(int protocol) {
        fd_ = ::socket(PF_NETLINK, SOCK_RAW, protocol);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to create netlink socket");
        }

        int rcvbuf = 1024 * 1024;
        ::setsockopt(fd_, SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf));

        sockaddr_nl sa{};
        sa.nl_family = AF_NETLINK;
        sa.nl_groups = 1;

        if (::bind(fd_, reinterpret_cast<sockaddr*>(&sa), sizeof(sa)) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "Failed to bind netlink socket");
        }
    }

    ~NetlinkSocket() {
        if (fd_ >= 0) ::close(fd_);
    }

    NetlinkSocket(const NetlinkSocket&) = delete;
    NetlinkSocket& operator=(const NetlinkSocket&) = delete;

    [[nodiscard]] int get() const noexcept { return fd_; }
};

struct UeventPayload {
    std::string action;
    std::string devname;
    unsigned int major_num = 0;
    unsigned int minor_num = 0;
};

static void inspect_node(const UeventPayload& event) {
    fs::path full_path = fs::path("/dev") / event.devname;

    struct stat st;
    if (::lstat(full_path.c_str(), &st) < 0) {
        std::cerr << "  [VFS Check] Failed to lstat path: " << full_path << " (Node absent in devtmpfs)\n";
        return;
    }

    const unsigned int actual_maj = major(st.st_rdev);
    const unsigned int actual_min = minor(st.st_rdev);
    const std::string_view type_str = S_ISCHR(st.st_mode) ? "CHARACTER" :
                                      S_ISBLK(st.st_mode) ? "BLOCK" : "OTHER";

    std::cout << "  [VFS Check] Path: " << full_path.string() << "\n"
              << "              Type: " << type_str << " | Mode: 0" << std::oct << (st.st_mode & 07777) << std::dec
              << " | UID: " << st.st_uid << " | GID: " << st.st_gid << "\n"
              << "              Major:Minor -> Kernel: " << event.major_num << ":" << event.minor_num
              << " | devtmpfs: " << actual_maj << ":" << actual_min << "\n";

    if (actual_maj == event.major_num && actual_min == event.minor_num) {
        std::cout << "              STATUS: MATCH (Verified)\n";
    } else {
        std::cout << "              STATUS: MISMATCH!\n";
    }
}

int main() {
    try {
        NetlinkSocket socket(NETLINK_KOBJECT_UEVENT);
        std::cout << "=== [C++] Listening for Kernel Uevents and inspecting devtmpfs (/dev) ===\n";

        std::vector<char> buffer(8192);
        while (true) {
            ssize_t len = ::recv(socket.get(), buffer.data(), buffer.size() - 1, 0);
            if (len <= 0) {
                if (len < 0 && errno == EINTR) continue;
                break;
            }
            buffer[len] = '\0';   // остання пара KEY=VALUE теж мусить мати свій '\0'

            UeventPayload event;
            size_t offset = 0;

            while (offset < static_cast<size_t>(len)) {
                std::string_view item(buffer.data() + offset);
                if (item.starts_with("ACTION=")) {
                    event.action = item.substr(7);
                } else if (item.starts_with("DEVNAME=")) {
                    event.devname = item.substr(8);
                } else if (item.starts_with("MAJOR=")) {
                    event.major_num = std::stoul(std::string(item.substr(6)));
                } else if (item.starts_with("MINOR=")) {
                    event.minor_num = std::stoul(std::string(item.substr(6)));
                }
                offset += item.size() + 1;
            }

            if (!event.action.empty() && !event.devname.empty()) {
                std::cout << "\n[Uevent] Action: " << event.action << " | Devname: " << event.devname
                          << " | Major:Minor: " << event.major_num << ":" << event.minor_num << "\n";

                if (event.action == "add") {
                    // Оборонна пауза: ядро гарантує, що вузол уже створено (див. розбір нижче)
                    std::this_thread::sleep_for(std::chrono::milliseconds(1));
                    inspect_node(event);
                }
            }
        }
    } catch (const std::exception& ex) {
        std::cerr << "Fatal Error: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
