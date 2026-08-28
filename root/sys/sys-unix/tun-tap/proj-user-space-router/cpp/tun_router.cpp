// tun_router.cpp — Ідіоматична реалізація C++20 (RAII, span, std::expected/exceptions)
#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <system_error>
#include <string_view>
#include <cstring>
#include <cstdint>

#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/epoll.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <linux/if.h>
#include <linux/if_tun.h>

namespace tuntap {

// RAII обгортка над дескриптором TUN-пристрою
class TunDevice {
private:
    int fd_{-1};
    std::string name_;

public:
    explicit TunDevice(std::string_view dev_name, int flags = IFF_TUN | IFF_NO_PI) {
        fd_ = ::open("/dev/net/tun", O_RDWR | O_NONBLOCK);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to open /dev/net/tun");
        }

        struct ifreq ifr{};
        ifr.ifr_flags = static_cast<short>(flags);
        if (!dev_name.empty()) {
            std::strncpy(ifr.ifr_name, dev_name.data(), IFNAMSIZ - 1);
        }

        if (::ioctl(fd_, TUNSETIFF, reinterpret_cast<void*>(&ifr)) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "ioctl(TUNSETIFF) failed");
        }

        name_ = ifr.ifr_name;
    }

    ~TunDevice() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    TunDevice(const TunDevice&) = delete;
    TunDevice& operator=(const TunDevice&) = delete;

    TunDevice(TunDevice&& other) noexcept : fd_(other.fd_), name_(std::move(other.name_)) {
        other.fd_ = -1;
    }

    TunDevice& operator=(TunDevice&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            name_ = std::move(other.name_);
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }
    [[nodiscard]] const std::string& name() const noexcept { return name_; }

    [[nodiscard]] std::ssize_t read(std::span<std::uint8_t> buffer) const {
        return ::read(fd_, buffer.data(), buffer.size());
    }

    [[nodiscard]] std::ssize_t write(std::span<const std::uint8_t> packet) const {
        return ::write(fd_, packet.data(), packet.size());
    }
};

// RAII обгортка над epoll
class EpollSelector {
private:
    int epoll_fd_{-1};

public:
    EpollSelector() {
        epoll_fd_ = ::epoll_create1(0);
        if (epoll_fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "epoll_create1 failed");
        }
    }

    ~EpollSelector() noexcept {
        if (epoll_fd_ >= 0) ::close(epoll_fd_);
    }

    void add_fd(int fd, std::uint32_t events) {
        struct epoll_event ev{};
        ev.events = events;
        ev.data.fd = fd;
        if (::epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, fd, &ev) < 0) {
            throw std::system_error(errno, std::generic_category(), "epoll_ctl ADD failed");
        }
    }

    [[nodiscard]] int wait(std::span<struct epoll_event> events_out, int timeout_ms) const {
        return ::epoll_wait(epoll_fd_, events_out.data(), static_cast<int>(events_out.size()), timeout_ms);
    }
};

// Обчислення контрольної суми
uint16_t calculate_checksum(std::span<const std::uint8_t> data) {
    std::uint32_t sum = 0;
    std::size_t i = 0;
    while (i + 1 < data.size()) {
        std::uint16_t word = static_cast<std::uint16_t>(data[i]) | (static_cast<std::uint16_t>(data[i+1]) << 8);
        sum += word;
        i += 2;
    }
    if (i < data.size()) {
        sum += data[i];
    }
    while (sum >> 16) {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }
    return static_cast<std::uint16_t>(~sum);
}

void process_icmp_reply(const TunDevice& tun, std::span<std::uint8_t> pkt) {
    if (pkt.size() < sizeof(struct iphdr)) return;

    auto* iph = reinterpret_cast<struct iphdr*>(pkt.data());
    if (iph->version != 4 || iph->protocol != IPPROTO_ICMP) return;

    std::size_t ip_hdr_len = iph->ihl * 4;
    if (pkt.size() < ip_hdr_len + sizeof(struct icmphdr)) return;

    auto* icmph = reinterpret_cast<struct icmphdr*>(pkt.data() + ip_hdr_len);
    if (icmph->type == ICMP_ECHO) {
        std::swap(iph->saddr, iph->daddr);
        icmph->type = ICMP_ECHOREPLY;
        icmph->checksum = 0;

        icmph->checksum = calculate_checksum(pkt.subspan(ip_hdr_len));
        iph->check = 0;
        iph->check = calculate_checksum(pkt.subspan(0, ip_hdr_len));

        std::ssize_t sent = tun.write(pkt);
        if (sent > 0) {
            std::cout << "[C++] Generated ICMP Echo Reply (" << sent << " bytes)\n";
        }
    }
}

} // namespace tuntap

int main() {
    try {
        tuntap::TunDevice tun("tun0");
        std::cout << "[C++] Virtual interface initialized: " << tun.name() << "\n";

        tuntap::EpollSelector selector;
        selector.add_fd(tun.native_handle(), EPOLLIN | EPOLLET);

        std::vector<std::uint8_t> buffer(2048);
        std::vector<struct epoll_event> events(8);

        for (int i = 0; i < 5; ++i) {
            int nfds = selector.wait(events, 5000);
            for (int n = 0; n < nfds; ++n) {
                if (events[n].data.fd == tun.native_handle()) {
                    while (true) {
                        std::ssize_t nread = tun.read(buffer);
                        if (nread < 0) {
                            if (errno == EAGAIN || errno == EWOULDBLOCK) break;
                            perror("read error");
                            break;
                        }
                        tuntap::process_icmp_reply(tun, std::span<std::uint8_t>(buffer.data(), nread));
                    }
                }
            }
        }
    } catch (const std::exception& ex) {
        std::cerr << "Fatal error: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
