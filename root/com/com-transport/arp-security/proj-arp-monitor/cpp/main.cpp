#include <iostream>
#include <array>
#include <vector>
#include <unordered_map>
#include <chrono>
#include <span>
#include <string>
#include <string_view>
#include <sstream>
#include <iomanip>
#include <csignal>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <netinet/if_ether.h>
#include <linux/if_packet.h>

namespace net::security {

using MacAddress = std::array<uint8_t, 6>;
using Ipv4Address = std::array<uint8_t, 4>;

struct Ipv4Hash {
    std::size_t operator()(const Ipv4Address& ip) const noexcept {
        uint32_t val;
        std::memcpy(&val, ip.data(), 4);
        return std::hash<uint32_t>{}(val);
    }
};

std::string format_mac(const MacAddress& mac) {
    std::ostringstream ss;
    ss << std::hex << std::setfill('0');
    for (size_t i = 0; i < mac.size(); ++i) {
        if (i > 0) ss << ":";
        ss << std::setw(2) << static_cast<int>(mac[i]);
    }
    return ss.str();
}

std::string format_ip(const Ipv4Address& ip) {
    char buf[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, ip.data(), buf, sizeof(buf));
    return std::string(buf);
}

class RawSocket {
public:
    explicit RawSocket(std::string_view if_name) {
        fd_ = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ARP));
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити AF_PACKET сокет");
        }

        struct ifreq ifr{};
        std::strncpy(ifr.ifr_name, if_name.data(), IFNAMSIZ - 1);
        if (ioctl(fd_, SIOCGIFINDEX, &ifr) < 0) {
            close(fd_);
            throw std::system_error(errno, std::generic_category(), "Не вдалося отримати ifindex");
        }

        struct sockaddr_ll sll{};
        sll.sll_family = AF_PACKET;
        sll.sll_ifindex = ifr.ifr_ifindex;
        sll.sll_protocol = htons(ETH_P_ARP);

        if (bind(fd_, reinterpret_cast<struct sockaddr*>(&sll), sizeof(sll)) < 0) {
            close(fd_);
            throw std::system_error(errno, std::generic_category(), "Не вдалося прив'язати сокет");
        }
    }

    ~RawSocket() {
        if (fd_ >= 0) {
            close(fd_);
        }
    }

    RawSocket(const RawSocket&) = delete;
    RawSocket& operator=(const RawSocket&) = delete;
    RawSocket(RawSocket&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    RawSocket& operator=(RawSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    ssize_t receive(std::span<uint8_t> buffer) const {
        return recvfrom(fd_, buffer.data(), buffer.size(), 0, nullptr, nullptr);
    }

private:
    int fd_{-1};
};

struct HostState {
    MacAddress mac{};
    std::chrono::steady_clock::time_point last_seen{};
    int garp_count{0};
    std::chrono::steady_clock::time_point garp_window_start{};
};

class ArpInspector {
public:
    ArpInspector(Ipv4Address gw_ip, MacAddress gw_mac)
        : gateway_ip_(gw_ip), gateway_mac_(gw_mac), has_gateway_(true) {}

    ArpInspector() : has_gateway_(false) {}

    void process_frame(std::span<const uint8_t> frame) {
        if (frame.size() < sizeof(struct ethhdr) + sizeof(struct ether_arp)) {
            return;
        }

        const auto* eth = reinterpret_cast<const struct ethhdr*>(frame.data());
        const auto* arp = reinterpret_cast<const struct ether_arp*>(frame.data() + sizeof(struct ethhdr));

        if (ntohs(eth->h_proto) != ETH_P_ARP) return;

        uint16_t htype = ntohs(arp->ea_hdr.ar_hrd);
        uint16_t ptype = ntohs(arp->ea_hdr.ar_pro);
        uint16_t opcode = ntohs(arp->ea_hdr.ar_op);

        if (htype != ARPHRD_ETHER || ptype != ETHERTYPE_IP) return;

        MacAddress eth_src{};
        MacAddress arp_sha{};
        Ipv4Address sender_ip{};
        Ipv4Address target_ip{};

        std::memcpy(eth_src.data(), eth->h_source, 6);
        std::memcpy(arp_sha.data(), arp->arp_sha, 6);
        std::memcpy(sender_ip.data(), arp->arp_spa, 4);
        std::memcpy(target_ip.data(), arp->arp_tpa, 4);

        auto now = std::chrono::steady_clock::now();

        // Перевірка 1: Відповідність Eth Src та ARP SHA
        if (eth_src != arp_sha) {
            std::cout << "[АЛАРМ: ПІДМІНА ЗАГОЛОВКА] Eth Src (" << format_mac(eth_src)
                      << ") != ARP SHA (" << format_mac(arp_sha)
                      << ") для IP " << format_ip(sender_ip) << "\n";
        }

        // Перевірка 2: Захист шлюзу за замовчуванням
        if (has_gateway_ && sender_ip == gateway_ip_) {
            if (arp_sha != gateway_mac_) {
                std::cout << "[КРИТИЧНИЙ АЛАРМ: ARP SPOOFING ШЛЮЗУ] Хост " << format_mac(arp_sha)
                          << " заявив права на IP шлюзу " << format_ip(sender_ip)
                          << "! Легітимний MAC: " << format_mac(gateway_mac_) << "\n";
                return;
            }
        }

        // Перевірка 3: Станковий аналіз таблиці прив'язок
        auto it = table_.find(sender_ip);
        if (it == table_.end()) {
            table_[sender_ip] = HostState{arp_sha, now, 0, now};
        } else {
            auto& state = it->second;
            if (state.mac != arp_sha) {
                auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(now - state.last_seen).count();
                if (elapsed < 30) {
                    std::cout << "[АЛАРМ: MAC FLIP-FLOP] IP " << format_ip(sender_ip)
                              << " змінила прив'язку: " << format_mac(state.mac)
                              << " -> " << format_mac(arp_sha)
                              << " за " << elapsed << " с!\n";
                }
                state.mac = arp_sha;
            }
            state.last_seen = now;

            // Перевірка 4: Виявлення штормів Gratuitous ARP
            if (sender_ip == target_ip && opcode == ARPOP_REPLY) {
                auto window = std::chrono::duration_cast<std::chrono::milliseconds>(now - state.garp_window_start).count();
                if (window > 1000) {
                    state.garp_window_start = now;
                    state.garp_count = 1;
                } else {
                    state.garp_count++;
                    if (state.garp_count > 3) {
                        std::cout << "[АЛАРМ: ШТОРМ GARP] Хост " << format_ip(sender_ip)
                                  << " (" << format_mac(arp_sha) << ") надіслав "
                                  << state.garp_count << " GARP-відповідей за секунду!\n";
                    }
                }
            }
        }
    }

private:
    Ipv4Address gateway_ip_{};
    MacAddress gateway_mac_{};
    bool has_gateway_{false};
    std::unordered_map<Ipv4Address, HostState, Ipv4Hash> table_;
};

} // namespace net::security

static volatile std::sig_atomic_t g_running = 1;
void signal_handler(int) { g_running = 0; }

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <інтерфейс> [шлюз_IP] [шлюз_MAC]\n";
        return 1;
    }

    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    try {
        net::security::RawSocket sock(argv[1]);
        std::unique_ptr<net::security::ArpInspector> inspector;

        if (argc >= 4) {
            net::security::Ipv4Address gw_ip{};
            net::security::MacAddress gw_mac{};
            inet_pton(AF_INET, argv[2], gw_ip.data());
            std::sscanf(argv[3], "%hhx:%hhx:%hhx:%hhx:%hhx:%hhx",
                        &gw_mac[0], &gw_mac[1], &gw_mac[2], &gw_mac[3], &gw_mac[4], &gw_mac[5]);
            inspector = std::make_unique<net::security::ArpInspector>(gw_ip, gw_mac);
        } else {
            inspector = std::make_unique<net::security::ArpInspector>();
        }

        std::cout << "L2 ARP-монітор запущено на інтерфейсі " << argv[1] << "...\n";
        std::array<uint8_t, 2048> buffer{};

        while (g_running) {
            ssize_t len = sock.receive(buffer);
            if (len > 0) {
                inspector->process_frame(std::span<const uint8_t>(buffer.data(), static_cast<size_t>(len)));
            }
        }

        std::cout << "\nМонітор коректно завершив роботу.\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
