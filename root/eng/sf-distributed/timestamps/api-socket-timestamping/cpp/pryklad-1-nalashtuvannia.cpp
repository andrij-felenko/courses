#include <iostream>
#include <string_view>
#include <vector>
#include <array>
#include <span>
#include <memory>
#include <expected>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <linux/net_tstamp.h>
#include <linux/sockios.h>
#include <linux/errqueue.h>
#include <poll.h>

class SocketHandle {
    int fd_{-1};
public:
    explicit SocketHandle(int fd) noexcept : fd_(fd) {}
    ~SocketHandle() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;
    SocketHandle(SocketHandle&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    SocketHandle& operator=(SocketHandle&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }
};

struct TimestampReport {
    timespec software_ts{};
    timespec raw_hardware_ts{};
    uint32_t packet_seq_id{0};
};

class TimestampedSocket {
    SocketHandle sock_;

public:
    static std::expected<TimestampedSocket, std::error_code> create(std::string_view ifname) {
        int fd = ::socket(AF_INET, SOCK_DGRAM, 0);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        SocketHandle handle(fd);

        // Налаштування апаратного фільтра мережевої карти
        struct ifreq ifr{};
        std::strncpy(ifr.ifr_name, ifname.data(), sizeof(ifr.ifr_name) - 1);
        struct hwtstamp_config config{};
        config.tx_type = HWTSTAMP_TX_ON;
        config.rx_filter = HWTSTAMP_FILTER_ALL;
        ifr.ifr_data = reinterpret_cast<char*>(&config);

        if (::ioctl(handle.get(), SIOCSHWTSTAMP, &ifr) < 0) {
            std::cerr << "Попередження: SIOCSHWTSTAMP не підтримується для " << ifname << "\n";
        }

        // Конфігурація сокетних прапорців SO_TIMESTAMPING
        int flags = SOF_TIMESTAMPING_TX_HARDWARE |
                    SOF_TIMESTAMPING_TX_SOFTWARE |
                    SOF_TIMESTAMPING_RX_HARDWARE |
                    SOF_TIMESTAMPING_RX_SOFTWARE |
                    SOF_TIMESTAMPING_RAW_HARDWARE |
                    SOF_TIMESTAMPING_SOFTWARE |
                    SOF_TIMESTAMPING_OPT_ID |
                    SOF_TIMESTAMPING_OPT_TSONLY;

        if (::setsockopt(handle.get(), SOL_SOCKET, SO_TIMESTAMPING, &flags, sizeof(flags)) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return TimestampedSocket(std::move(handle));
    }

    explicit TimestampedSocket(SocketHandle sock) : sock_(std::move(sock)) {}

    std::expected<void, std::error_code> send(std::span<const std::byte> data, const sockaddr_in& dest) {
        ssize_t res = ::sendto(sock_.get(), data.data(), data.size(), 0,
                               reinterpret_cast<const sockaddr*>(&dest), sizeof(dest));
        if (res < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }

    std::expected<TimestampReport, std::error_code> receive_tx_timestamp(int timeout_ms = 500) {
        pollfd pfd{.fd = sock_.get(), .events = POLLERR, .revents = 0};
        int poll_res = ::poll(&pfd, 1, timeout_ms);
        if (poll_res <= 0) {
            return std::unexpected(std::make_error_code(std::errc::timed_out));
        }

        std::array<char, 512> ctrl_buf{};
        msghdr msg{};
        msg.msg_control = ctrl_buf.data();
        msg.msg_controllen = ctrl_buf.size();

        if (::recvmsg(sock_.get(), &msg, MSG_ERRQUEUE | MSG_DONTWAIT) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        TimestampReport report{};
        for (auto* cmsg = CMSG_FIRSTHDR(&msg); cmsg != nullptr; cmsg = CMSG_NXTHDR(&msg, cmsg)) {
            if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_TIMESTAMPING) {
                auto* ts = reinterpret_cast<struct scm_timestamping*>(CMSG_DATA(cmsg));
                report.software_ts = ts->ts[0];
                report.raw_hardware_ts = ts->ts[2];
            } else if (cmsg->cmsg_level == SOL_IP && cmsg->cmsg_type == IP_RECVERR) {
                auto* err = reinterpret_cast<struct sock_extended_err*>(CMSG_DATA(cmsg));
                report.packet_seq_id = err->ee_data;
            }
        }
        return report;
    }
};

int main(int argc, char* argv[]) {
    std::string_view ifname = (argc > 1) ? argv[1] : "eth0";

    auto sock_res = TimestampedSocket::create(ifname);
    if (!sock_res) {
        std::cerr << "Помилка ініціалізації сокета: " << sock_res.error().message() << "\n";
        return 1;
    }
    auto& ts_sock = *sock_res;

    sockaddr_in dest{};
    dest.sin_family = AF_INET;
    dest.sin_port = htons(12345);
    ::inet_pton(AF_INET, "127.0.0.1", &dest.sin_addr);

    std::string_view msg = "Тестове повідомлення C++";
    auto data_span = std::as_bytes(std::span(msg.data(), msg.size()));

    if (auto res = ts_sock.send(data_span, dest); !res) {
        std::cerr << "Помилка надсилання: " << res.error().message() << "\n";
        return 1;
    }
    std::cout << "Пакет надіслано. Очікування мітки часу...\n";

    auto ts_res = ts_sock.receive_tx_timestamp();
    if (!ts_res) {
        std::cerr << "Помилка отримання мітки: " << ts_res.error().message() << "\n";
        return 1;
    }

    const auto& rep = *ts_res;
    std::cout << "Успішно отримано мітку часу для пакета ID " << rep.packet_seq_id << ":\n"
              << "  Програмний час (SW): " << rep.software_ts.tv_sec << "." << rep.software_ts.tv_nsec << " с\n"
              << "  Апаратний час (HW):  " << rep.raw_hardware_ts.tv_sec << "." << rep.raw_hardware_ts.tv_nsec << " с\n";
    return 0;
}
