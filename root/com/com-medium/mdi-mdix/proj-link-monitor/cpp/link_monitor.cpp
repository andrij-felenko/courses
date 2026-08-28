// link_monitor.cpp — Ідіоматичний C++20 монітор фізичного рівня та Duplex Mismatch
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <chrono>
#include <thread>
#include <expected>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/sockios.h>
#include <linux/ethtool.h>

namespace net {

// RAII обгортка для файлового дескриптора діагностичного сокета
class SocketHandle {
    int m_fd{-1};
public:
    SocketHandle() : m_fd{::socket(AF_INET, SOCK_DGRAM, 0)} {}
    ~SocketHandle() {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
    }
    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;
    SocketHandle(SocketHandle&& other) noexcept : m_fd{other.m_fd} { other.m_fd = -1; }
    SocketHandle& operator=(SocketHandle&& other) noexcept {
        if (this != &other) {
            if (m_fd >= 0) ::close(m_fd);
            m_fd = other.m_fd;
            other.m_fd = -1;
        }
        return *this;
    }

    [[nodiscard]] bool is_valid() const noexcept { return m_fd >= 0; }
    [[nodiscard]] int native_handle() const noexcept { return m_fd; }
};

struct ErrorStats {
    uint64_t late_collisions{0};
    uint64_t crc_errors{0};
    uint64_t align_errors{0};
    uint64_t tx_packets{0};
};

struct LinkInfo {
    uint32_t speed_mbps{0};
    bool is_full_duplex{false};
    bool autoneg_enabled{false};
    std::string mdix_status;
};

class LinkMonitor {
    SocketHandle m_sock;
    std::string m_ifname;
    std::vector<std::string> m_stat_names;

public:
    explicit LinkMonitor(std::string_view ifname) : m_ifname{ifname} {
        if (!m_sock.is_valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити діагностичний сокет");
        }
        load_stat_strings();
    }

    [[nodiscard]] std::expected<LinkInfo, std::error_code> get_link_info() const {
        ethtool_cmd ecmd{};
        ecmd.cmd = ETHTOOL_GSET;

        ifreq ifr{};
        std::strncpy(ifr.ifr_name, m_ifname.c_str(), IFNAMSIZ - 1);
        ifr.ifr_data = reinterpret_cast<char*>(&ecmd);

        if (::ioctl(m_sock.native_handle(), SIOCETHTOOL, &ifr) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        LinkInfo info;
        uint32_t sp = ethtool_cmd_speed(&ecmd);
        info.speed_mbps = (sp == static_cast<uint32_t>(-1)) ? 0 : sp;
        info.is_full_duplex = (ecmd.duplex == DUPLEX_FULL);
        info.autoneg_enabled = (ecmd.autoneg == AUTONEG_ENABLE);

        switch (ecmd.eth_tp_mdix) {
            case ETH_TP_MDI:   info.mdix_status = "MDI (прямий)"; break;
            case ETH_TP_MDI_X: info.mdix_status = "MDI-X (перехресний)"; break;
            default:           info.mdix_status = "Автовизначення / Не підтримується"; break;
        }

        return info;
    }

    [[nodiscard]] std::expected<ErrorStats, std::error_code> read_error_stats() const {
        if (m_stat_names.empty()) {
            return ErrorStats{};
        }

        size_t sz = sizeof(ethtool_stats) + m_stat_names.size() * sizeof(uint64_t);
        std::vector<uint8_t> buffer(sz);
        auto* stats = reinterpret_cast<ethtool_stats*>(buffer.data());
        stats->cmd = ETHTOOL_GSTATS;
        stats->n_stats = static_cast<uint32_t>(m_stat_names.size());

        ifreq ifr{};
        std::strncpy(ifr.ifr_name, m_ifname.c_str(), IFNAMSIZ - 1);
        ifr.ifr_data = reinterpret_cast<char*>(stats);

        if (::ioctl(m_sock.native_handle(), SIOCETHTOOL, &ifr) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        ErrorStats errs;
        for (size_t i = 0; i < m_stat_names.size(); ++i) {
            const auto& name = m_stat_names[i];
            uint64_t val = stats->data[i];

            if (name.find("late_collision") != std::string::npos) {
                errs.late_collisions += val;
            } else if (name.find("crc_error") != std::string::npos || name.find("rx_crc_errors") != std::string::npos) {
                errs.crc_errors += val;
            } else if (name.find("align_error") != std::string::npos) {
                errs.align_errors += val;
            } else if (name.find("tx_packets") != std::string::npos || name.find("tx_ok") != std::string::npos) {
                errs.tx_packets += val;
            }
        }
        return errs;
    }

private:
    void load_stat_strings() {
        struct {
            ethtool_sset_info hdr;
            uint32_t buf[1];
        } sset_info{};
        sset_info.hdr.cmd = ETHTOOL_GSSET_INFO;
        sset_info.hdr.sset_mask = 1ULL << ETH_SS_STATS;

        ifreq ifr{};
        std::strncpy(ifr.ifr_name, m_ifname.c_str(), IFNAMSIZ - 1);
        ifr.ifr_data = reinterpret_cast<char*>(&sset_info);

        if (::ioctl(m_sock.native_handle(), SIOCETHTOOL, &ifr) < 0 || !sset_info.hdr.sset_mask) {
            return;
        }

        uint32_t count = sset_info.hdr.data[0];
        if (count == 0) return;

        size_t sz = sizeof(ethtool_gstrings) + count * ETH_GSTRING_LEN;
        std::vector<uint8_t> str_buf(sz);
        auto* gstrings = reinterpret_cast<ethtool_gstrings*>(str_buf.data());
        gstrings->cmd = ETHTOOL_GSTRINGS;
        gstrings->string_set = ETH_SS_STATS;
        gstrings->len = count;

        ifr.ifr_data = reinterpret_cast<char*>(gstrings);
        if (::ioctl(m_sock.native_handle(), SIOCETHTOOL, &ifr) == 0) {
            m_stat_names.reserve(count);
            for (uint32_t i = 0; i < count; ++i) {
                const char* s = reinterpret_cast<const char*>(&gstrings->data[i * ETH_GSTRING_LEN]);
                m_stat_names.emplace_back(s);
            }
        }
    }
};

} // namespace net

int main(int argc, char** argv) {
    const std::string ifname = (argc > 1) ? argv[1] : "eth0";

    try {
        net::LinkMonitor monitor{ifname};
        auto link_res = monitor.get_link_info();

        if (!link_res) {
            std::cerr << "Помилка отримання статусу лінка: " << link_res.error().message() << '\n';
            return 1;
        }

        const auto& info = *link_res;
        std::cout << "=== Інтерфейс " << ifname << " ===\n"
                  << "Швидкість:      " << (info.speed_mbps == 0 ? "Link Down" : std::to_string(info.speed_mbps) + " Мбіт/с") << '\n'
                  << "Дуплекс:        " << (info.is_full_duplex ? "Full Duplex" : "Half Duplex") << '\n'
                  << "Автопогодження: " << (info.autoneg_enabled ? "Увімкнено" : "Вимкнено") << '\n'
                  << "MDI/MDI-X стан: " << info.mdix_status << "\n\n"
                  << "Моніторинг лічильників Duplex Mismatch (10 ітерацій)...\n";

        auto prev_stats = monitor.read_error_stats().value_or(net::ErrorStats{});

        for (int i = 1; i <= 10; ++i) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
            auto curr_res = monitor.read_error_stats();
            if (!curr_res) break;

            const auto& curr = *curr_res;
            uint64_t d_late = curr.late_collisions - prev_stats.late_collisions;
            uint64_t d_crc = curr.crc_errors - prev_stats.crc_errors;

            if (d_late > 0 || d_crc > 0) {
                std::cout << "[УВАГА +" << i << "s] Пізні колізії: +" << d_late
                          << ", CRC помилки: +" << d_crc << " -> ";
                if (d_late > 5 && !info.is_full_duplex) {
                    std::cout << "КРИТИЧНО: Duplex Mismatch (локальний у Half Duplex, партнер у Full Duplex)!\n";
                } else if (d_crc > 5 && info.is_full_duplex) {
                    std::cout << "КРИТИЧНО: Duplex Mismatch (локальний у Full Duplex, партнер у Half Duplex)!\n";
                } else {
                    std::cout << "Поодинокі помилки кадру лінії.\n";
                }
            } else {
                std::cout << "[OK +" << i << "s] Помилок немає.\n";
            }
            prev_stats = curr;
        }

    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
