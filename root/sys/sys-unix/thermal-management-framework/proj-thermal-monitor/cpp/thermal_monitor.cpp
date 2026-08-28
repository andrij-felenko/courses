// thermal_monitor.cpp — Ідіоматичний системний термальний монітор мовою C++20 (RAII, Expected/Exceptions, StringView)
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <optional>
#include <filesystem>
#include <system_error>
#include <array>
#include <cstdint>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/genetlink.h>
#include <linux/thermal.h>

namespace fs = std::filesystem;

// RAII-обгортка для управління ресурсом мережевого сокета Netlink
class ThermalNetlinkSocket {
public:
    explicit ThermalNetlinkSocket(uint32_t multicast_groups = 1) {
        m_fd = ::socket(AF_NETLINK, SOCK_RAW, NETLINK_GENERIC);
        if (m_fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to create AF_NETLINK socket");
        }

        // Збільшення розміру буфера прийому для запобігання втраті подій
        int rcvbuf = 256 * 1024;
        ::setsockopt(m_fd, SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf));

        struct sockaddr_nl local{};
        local.nl_family = AF_NETLINK;
        local.nl_groups = multicast_groups;

        if (::bind(m_fd, reinterpret_cast<struct sockaddr*>(&local), sizeof(local)) < 0) {
            ::close(m_fd);
            throw std::system_error(errno, std::generic_category(), "Failed to bind Netlink socket");
        }
    }

    ~ThermalNetlinkSocket() noexcept {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
    }

    // Заборона копіювання для збереження суворої власності RAII
    ThermalNetlinkSocket(const ThermalNetlinkSocket&) = delete;
    ThermalNetlinkSocket& operator=(const ThermalNetlinkSocket&) = delete;

    // Дозвіл переміщення
    ThermalNetlinkSocket(ThermalNetlinkSocket&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }

    [[nodiscard]] int get_fd() const noexcept { return m_fd; }

    [[nodiscard]] std::vector<std::uint8_t> receive_event(std::size_t buffer_size = 8192) const {
        std::vector<std::uint8_t> buffer(buffer_size);
        ssize_t bytes = ::recv(m_fd, buffer.data(), buffer.size(), 0);
        
        if (bytes < 0) {
            if (errno == EINTR) return {};   // перерваний сигналом виклик — не помилка
            throw std::system_error(errno, std::generic_category(), "recv() failed");
        }
        
        buffer.resize(static_cast<std::size_t>(bytes));
        return buffer;
    }

private:
    int m_fd{-1};
};

// Клас інспекції атрибутів термальних зон у sysfs
class SysfsThermalInspector {
public:
    static std::optional<double> read_temperature(unsigned int zone_id) {
        const auto path = fs::path("/sys/class/thermal") / ("thermal_zone" + std::to_string(zone_id)) / "temp";
        std::ifstream file(path);
        if (!file.is_open()) return std::nullopt;

        long temp_mC = 0;
        if (file >> temp_mC) {
            return static_cast<double>(temp_mC) / 1000.0;
        }
        return std::nullopt;
    }

    static std::optional<std::string> read_zone_type(unsigned int zone_id) {
        const auto path = fs::path("/sys/class/thermal") / ("thermal_zone" + std::to_string(zone_id)) / "type";
        std::ifstream file(path);
        if (!file.is_open()) return std::nullopt;

        std::string type;
        std::getline(file, type);
        return type;
    }
};

// Головний клас керування моніторингом
class ThermalMonitorApp {
public:
    void run_sysfs_scan() const {
        std::cout << "=== Сканування термальних зон у sysfs ===\n";
        for (unsigned int zone = 0; zone < 4; ++zone) {
            const auto type = SysfsThermalInspector::read_zone_type(zone);
            const auto temp = SysfsThermalInspector::read_temperature(zone);

            if (type && temp) {
                std::cout << "Зона " << zone << " [" << *type << "]: "
                          << *temp << " °C\n";
            }
        }
    }

    void start_event_loop() const {
        try {
            ThermalNetlinkSocket nl_socket(1);
            std::cout << "\n[Netlink] Асинхронний монітор запущено. Очікування подій ядра...\n";

            while (true) {
                const auto raw_data = nl_socket.receive_event();
                process_netlink_payload(raw_data);
            }
        } catch (const std::exception& ex) {
            std::cerr << "[Помилка моніторингу]: " << ex.what() << '\n';
        }
    }

private:
    void process_netlink_payload(const std::vector<std::uint8_t>& payload) const {
        if (payload.size() < sizeof(struct nlmsghdr)) return;

        const auto* nlh = reinterpret_cast<const struct nlmsghdr*>(payload.data());
        if (nlh->nlmsg_type == NLMSG_ERROR) return;

        const auto* gnlh = reinterpret_cast<const struct genlmsghdr*>(NLMSG_DATA(nlh));
        std::cout << "[C++ Event] Команда події ядра: 0x" << std::hex 
                  << static_cast<int>(gnlh->cmd) << std::dec << '\n';
    }
};

int main() {
    std::cout << "=== Термальний монітор ядра Linux (C++20 RAII & Netlink) ===\n\n";

    ThermalMonitorApp app;
    app.run_sysfs_scan();
    app.start_event_loop();

    return 0;
}
