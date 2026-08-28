// rport_monitor.cpp — ідіоматичний моніторинг подій транспорту SCSI на C++20.
// Складання: g++ -std=c++20 -O2 -Wall -Wextra rport_monitor.cpp -o rport_monitor
#include <iostream>
#include <string>
#include <string_view>
#include <array>
#include <span>
#include <chrono>
#include <format>
#include <fstream>
#include <filesystem>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>

namespace fs = std::filesystem;

class NetlinkSocket {
public:
    explicit NetlinkSocket(int protocol) {
        fd_ = ::socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, protocol);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "socket(AF_NETLINK) failed");
        }

        sockaddr_nl sa{};
        sa.nl_family = AF_NETLINK;
        sa.nl_groups = 1; // Broadcast uevents

        if (::bind(fd_, reinterpret_cast<sockaddr*>(&sa), sizeof(sa)) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "bind(netlink) failed");
        }
    }

    ~NetlinkSocket() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    NetlinkSocket(const NetlinkSocket&) = delete;
    NetlinkSocket& operator=(const NetlinkSocket&) = delete;
    NetlinkSocket(NetlinkSocket&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    NetlinkSocket& operator=(NetlinkSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] ssize_t receive(std::span<char> buffer) const {
        return ::recv(fd_, buffer.data(), buffer.size(), 0);
    }

private:
    int fd_{-1};
};

static std::string read_sysfs(const fs::path& devpath, std::string_view attr) {
    fs::path full_path = fs::path("/sys") / devpath.relative_path() / attr;
    std::ifstream file(full_path);
    if (!file.is_open()) {
        return "<недоступно>";
    }
    std::string val;
    std::getline(file, val);
    return val.empty() ? "<порожньо>" : val;
}

int main() {
    try {
        NetlinkSocket socket(NETLINK_KOBJECT_UEVENT);
        std::cout << "=== Запущено моніторинг подій SCSI транспорту (C++20) ===\n";
        std::cout << "Очікування uevent... Для виходу натисніть Ctrl+C\n\n";

        std::array<char, 4096> buffer{};

        while (true) {
            ssize_t len = socket.receive(buffer);
            if (len <= 0) continue;

            std::string_view action{};
            std::string_view devpath{};
            std::string_view subsystem{};

            size_t offset = 0;
            while (offset < static_cast<size_t>(len)) {
                std::string_view entry(buffer.data() + offset);
                if (entry.starts_with("ACTION=")) {
                    action = entry.substr(7);
                } else if (entry.starts_with("DEVPATH=")) {
                    devpath = entry.substr(8);
                } else if (entry.starts_with("SUBSYSTEM=")) {
                    subsystem = entry.substr(10);
                }
                offset += entry.size() + 1;
            }

            if (subsystem == "fc_remote_ports" || subsystem == "iscsi_session") {
                const auto now = std::chrono::system_clock::now();
                std::cout << std::format("[{:%Y-%m-%d %H:%M:%S}] ПОДІЯ: дія={} | підсистема={} | шлях={}\n",
                                         now, action, subsystem, devpath);

                if (subsystem == "fc_remote_ports" && !devpath.empty()) {
                    fs::path p(devpath);
                    auto state = read_sysfs(p, "port_state");
                    auto fast_io = read_sysfs(p, "fast_io_fail_tmo");
                    auto dev_loss = read_sysfs(p, "dev_loss_tmo");
                    auto port_name = read_sysfs(p, "port_name");

                    std::cout << std::format("       └─ WWPN: {} | Стан: {} | fast_io_fail_tmo: {} с | dev_loss_tmo: {} с\n",
                                             port_name, state, fast_io, dev_loss);
                } else if (subsystem == "iscsi_session" && !devpath.empty()) {
                    fs::path p(devpath);
                    auto state = read_sysfs(p, "state");
                    auto recovery = read_sysfs(p, "recovery_tmo");
                    auto target = read_sysfs(p, "targetname");

                    std::cout << std::format("       └─ Target: {} | Стан: {} | recovery_tmo: {} с\n",
                                             target, state, recovery);
                }
                std::cout << std::flush;
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
