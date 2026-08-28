#include <iostream>
#include <array>
#include <span>
#include <vector>
#include <memory>
#include <chrono>
#include <expected>
#include <string_view>
#include <cstring>

#include <unistd.h>
#include <fcntl.h>
#include <poll.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <linux/sockios.h>
#include <linux/net_tstamp.h>
#include <linux/ptp_clock.h>

namespace ptp {

constexpr uint16_t EventPort = 319;
constexpr std::string_view MulticastGroup = "224.0.1.129";

struct PtpTimestamp {
    int64_t seconds{0};
    int64_t nanoseconds{0};
};

class UniqueFd {
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() { if (fd_ >= 0) ::close(fd_); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    UniqueFd& operator=(UniqueFd&& other) noexcept {
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
    int fd_{-1};
};

class PtpHardwareClock {
public:
    static std::expected<PtpHardwareClock, std::string> open(std::string_view path) {
        int fd = ::open(path.data(), O_RDWR);
        if (fd < 0) {
            return std::unexpected("Неможливо відкрити пристрій PHC: " + std::string(path));
        }
        return PtpHardwareClock(UniqueFd(fd));
    }

    [[nodiscard]] std::expected<PtpTimestamp, std::string> get_time() const {
        clockid_t clkid = get_clockid();
        struct timespec ts{};
        if (::clock_gettime(clkid, &ts) < 0) {
            return std::unexpected("Помилка clock_gettime для PHC");
        }
        return PtpTimestamp{ts.tv_sec, ts.tv_nsec};
    }

    [[nodiscard]] std::expected<void, std::string> adjust_frequency(double ppb) const {
        clockid_t clkid = get_clockid();
        struct timex tx{};
        tx.modes = ADJ_FREQUENCY;
        tx.freq = static_cast<long>(ppb * 65.536);
        if (::clock_adjtime(clkid, &tx) < 0) {
            return std::unexpected("Помилка clock_adjtime ADJ_FREQUENCY");
        }
        return {};
    }

private:
    explicit PtpHardwareClock(UniqueFd fd) : fd_(std::move(fd)) {}

    [[nodiscard]] clockid_t get_clockid() const noexcept {
        return static_cast<clockid_t>((((~static_cast<unsigned int>(fd_.get())) << 3) | 3));
    }

    UniqueFd fd_;
};

class PtpSocket {
public:
    static std::expected<PtpSocket, std::string> create(std::string_view ifname) {
        int fd = ::socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
        if (fd < 0) {
            return std::unexpected("Помилка створення сокета");
        }
        UniqueFd sock(fd);

        int reuse = 1;
        ::setsockopt(sock.get(), SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));

        sockaddr_in bind_addr{};
        bind_addr.sin_family = AF_INET;
        bind_addr.sin_port = htons(EventPort);
        bind_addr.sin_addr.s_addr = htonl(INADDR_ANY);
        if (::bind(sock.get(), reinterpret_cast<sockaddr*>(&bind_addr), sizeof(bind_addr)) < 0) {
            return std::unexpected("Помилка bind на порт 319");
        }

        // Конфігурація PHY таймстемпінгу
        struct hwtstamp_config cfg{};
        cfg.tx_type = HWTSTAMP_TX_ON;
        cfg.rx_filter = HWTSTAMP_FILTER_PTP_V2_EVENT;

        struct ifreq ifr{};
        std::strncpy(ifr.ifr_name, ifname.data(), sizeof(ifr.ifr_name) - 1);
        ifr.ifr_data = reinterpret_cast<char*>(&cfg);
        ::ioctl(sock.get(), SIOCSHWTSTAMP, &ifr);

        // Увімкнення прапорців SO_TIMESTAMPING
        int ts_flags = SOF_TIMESTAMPING_TX_HARDWARE |
                       SOF_TIMESTAMPING_RX_HARDWARE |
                       SOF_TIMESTAMPING_RAW_HARDWARE |
                       SOF_TIMESTAMPING_OPT_TSONLY;
        if (::setsockopt(sock.get(), SOL_SOCKET, SO_TIMESTAMPING, &ts_flags, sizeof(ts_flags)) < 0) {
            return std::unexpected("Помилка setsockopt SO_TIMESTAMPING");
        }

        return PtpSocket(std::move(sock));
    }

    [[nodiscard]] std::expected<void, std::string> send_sync() {
        std::array<uint8_t, 44> sync_packet{};
        sync_packet[0] = 0x00; // Sync
        sync_packet[1] = 0x02; // Version 2
        sync_packet[2] = 0x00;
        sync_packet[3] = 44;   // Length
        sync_packet[6] = 0x02; // Two-step

        sockaddr_in dst{};
        dst.sin_family = AF_INET;
        dst.sin_port = htons(EventPort);
        ::inet_pton(AF_INET, MulticastGroup.data(), &dst.sin_addr);

        ssize_t sent = ::sendto(sock_.get(), sync_packet.data(), sync_packet.size(), 0,
                                reinterpret_cast<sockaddr*>(&dst), sizeof(dst));
        if (sent < 0) {
            return std::unexpected("Помилка sendto для Sync");
        }
        return {};
    }

    [[nodiscard]] std::expected<PtpTimestamp, std::string> fetch_tx_timestamp() {
        pollfd pfd{};
        pfd.fd = sock_.get();
        pfd.events = POLLERR | POLLPRI;

        int res = ::poll(&pfd, 1, 500);
        if (res <= 0 || !(pfd.revents & (POLLERR | POLLPRI))) {
            return std::unexpected("Таймаут очікування мітки TX у MSG_ERRQUEUE");
        }

        std::array<char, 512> control{};
        std::array<uint8_t, 256> dummy{};
        iovec iov{dummy.data(), dummy.size()};
        msghdr msg{};
        msg.msg_iov = &iov;
        msg.msg_iovlen = 1;
        msg.msg_control = control.data();
        msg.msg_controllen = control.size();

        if (::recvmsg(sock_.get(), &msg, MSG_ERRQUEUE) < 0) {
            return std::unexpected("Помилка recvmsg MSG_ERRQUEUE");
        }

        for (auto* cmsg = CMSG_FIRSTHDR(&msg); cmsg != nullptr; cmsg = CMSG_NXTHDR(&msg, cmsg)) {
            if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_TIMESTAMPING) {
                auto* ts = reinterpret_cast<timespec*>(CMSG_DATA(cmsg));
                if (ts[2].tv_sec != 0 || ts[2].tv_nsec != 0) {
                    return PtpTimestamp{ts[2].tv_sec, ts[2].tv_nsec};
                }
            }
        }
        return std::unexpected("Апаратна мітка не знайдена в cmsg");
    }

private:
    explicit PtpSocket(UniqueFd sock) : sock_(std::move(sock)) {}

    UniqueFd sock_;
};

} // namespace ptp

int main(int argc, char* argv[]) {
    std::string_view ifname = (argc > 1) ? argv[1] : "eth0";
    std::string_view ptp_dev = (argc > 2) ? argv[2] : "/dev/ptp0";

    auto phc = ptp::PtpHardwareClock::open(ptp_dev);
    if (phc) {
        if (auto cur = phc->get_time(); cur) {
            std::cout << "Час PHC: " << cur->seconds << "." << cur->nanoseconds << " s\n";
        }
    }

    auto sock = ptp::PtpSocket::create(ifname);
    if (!sock) {
        std::cerr << "Помилка створення сокета: " << sock.error() << "\n";
        return EXIT_FAILURE;
    }

    if (auto sent = sock->send_sync(); !sent) {
        std::cerr << sent.error() << "\n";
        return EXIT_FAILURE;
    }

    if (auto tx_ts = sock->fetch_tx_timestamp(); tx_ts) {
        std::cout << "Апаратна мітка t1: " << tx_ts->seconds << "." << tx_ts->nanoseconds << " s\n";
    } else {
        std::cerr << tx_ts.error() << "\n";
    }

    return EXIT_SUCCESS;
}
